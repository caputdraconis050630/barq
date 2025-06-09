import os
import subprocess
import uuid
import json
import time
from typing import Dict, Any, Optional
from .runtime_interface import RuntimeInterface

class PythonRuntime(RuntimeInterface):

    def prepare(self, func_path: str, code: str, entrypoint: str):
        """Python 함수 실행을 위한 handler.py 파일을 생성합니다."""
        with open(os.path.join(func_path, "handler.py"), "w") as f:
            f.write(code)
        
        # entrypoint 정보를 metadata로 저장
        metadata = {"entrypoint": entrypoint}
        with open(os.path.join(func_path, "metadata.json"), "w") as f:
            json.dump(metadata, f)
    
    def run(self, func_path: str, event: Dict[str, Any]) -> str:
        """Python 함수를 Docker 컨테이너에서 실행합니다."""
        # event(사용자로부터 전달 받은 값) 저장
        event_path = os.path.join(func_path, "event.py")
        with open(event_path, "w") as f:
            f.write("event = " + str(event))
        
        # metadata에서 entrypoint 가져오기
        meta_path = os.path.join(func_path, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                metadata = json.load(f)
                entrypoint = metadata.get("entrypoint", "main")
        else:
            entrypoint = "main"
        
        # entrypoint 파싱 (예: "handler.main" -> module="handler", function="main")
        if "." in entrypoint:
            module_name, function_name = entrypoint.rsplit(".", 1)
        else:
            module_name = "handler"
            function_name = entrypoint
        
        exec_script = f"""
import json
from {module_name} import {function_name}
from event import event
result = {function_name}(event)
print(result)
"""
    
        with open(os.path.join(func_path, "run.py"), "w") as f:
            f.write(exec_script)
        
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(func_path)}:/app",
            "-w", "/app",
            "python:3.10",
            "python", "run.py"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return result.stderr.strip()
    
    # Warm Pool 구현
    def supports_warm_pool(self) -> bool:
        """Python 런타임은 warm pool을 지원합니다."""
        return True
    
    def warmup(self, func_id: str, func_path: str, code: str, entrypoint: str) -> Optional[str]:
        """
        Python 함수를 위한 warm 컨테이너를 시작합니다.
        컨테이너가 실행 상태로 유지되며, 함수 호출을 대기합니다.
        """
        try:
            # 함수 코드 준비
            self.prepare(func_path, code, entrypoint)
            
            # entrypoint 파싱
            if "." in entrypoint:
                module_name, function_name = entrypoint.rsplit(".", 1)
            else:
                module_name = "handler"
                function_name = entrypoint
            
            # warm 컨테이너를 위한 대기 스크립트 생성
            wait_script = f"""
import json
import os
import time
from {module_name} import {function_name}

print("WARM_CONTAINER_READY", flush=True)

# 이벤트 파일을 주기적으로 확인
while True:
    try:
        if os.path.exists("/app/event_input.json"):
            with open("/app/event_input.json", "r") as f:
                event_data = json.load(f)
            
            # 이벤트 파일 삭제 (처리됨을 표시)
            os.remove("/app/event_input.json")
            
            try:
                result = {function_name}(event_data)
                output = {{"result": result, "status": "success"}}
            except Exception as e:
                output = {{"result": str(e), "status": "error"}}
            
            # 결과를 파일에 저장
            with open("/app/event_output.json", "w") as f:
                json.dump(output, f)
                
        time.sleep(0.1)  # 100ms 대기
        
    except KeyboardInterrupt:
        break
    except Exception as e:
        with open("/app/event_output.json", "w") as f:
            json.dump({{"result": str(e), "status": "error"}}, f)
"""
            
            with open(os.path.join(func_path, "warm_run.py"), "w") as f:
                f.write(wait_script)
            
            # 백그라운드에서 실행되는 warm 컨테이너 시작
            container_name = f"warm-python-{func_id}-{uuid.uuid4().hex[:8]}"
            
            cmd = [
                "docker", "run", "-d", 
                "--name", container_name,
                "-v", f"{os.path.abspath(func_path)}:/app",
                "-w", "/app",
                "python:3.10",
                "python", "warm_run.py"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                
                # 컨테이너가 준비될 때까지 대기
                ready_cmd = ["docker", "logs", container_id]
                for _ in range(10):  # 최대 10초 대기
                    logs_result = subprocess.run(ready_cmd, capture_output=True, text=True)
                    if "WARM_CONTAINER_READY" in logs_result.stdout:
                        return container_id
                    time.sleep(1)
                
                # 준비되지 않으면 컨테이너 정리
                subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)
                return None
            else:
                return None
                
        except Exception as e:
            print(f"Error warming up container: {e}")
            return None
    
    def run_warm(self, container_id: str, event: Dict[str, Any]) -> str:
        """Warm 컨테이너에서 함수를 실행합니다."""
        try:
            # 이벤트를 JSON 파일로 저장
            event_json = json.dumps(event)
            
            # 컨테이너 내부에 이벤트 파일 생성
            cmd = ["docker", "exec", container_id, "/bin/bash", "-c", 
                   f"echo '{event_json}' > /app/event_input.json"]
            
            input_result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if input_result.returncode != 0:
                return f"Failed to send event to container: {input_result.stderr}"
            
            # 결과 파일이 생성될 때까지 대기 (최대 10초)
            for _ in range(100):  # 100 * 0.1 = 10초
                check_cmd = ["docker", "exec", container_id, "test", "-f", "/app/event_output.json"]
                check_result = subprocess.run(check_cmd, capture_output=True, text=True)
                
                if check_result.returncode == 0:
                    # 결과 파일 읽기
                    read_cmd = ["docker", "exec", container_id, "cat", "/app/event_output.json"]
                    read_result = subprocess.run(read_cmd, capture_output=True, text=True, timeout=5)
                    
                    if read_result.returncode == 0:
                        # 결과 파일 삭제
                        cleanup_cmd = ["docker", "exec", container_id, "rm", "/app/event_output.json"]
                        subprocess.run(cleanup_cmd, capture_output=True, text=True)
                        
                        try:
                            response_data = json.loads(read_result.stdout)
                            if response_data.get("status") == "success":
                                return str(response_data.get("result", ""))
                            else:
                                return f"Function error: {response_data.get('result', 'Unknown error')}"
                        except json.JSONDecodeError:
                            return read_result.stdout.strip()
                    break
                
                time.sleep(0.1)
            
            return "Function execution timeout in warm container"
                
        except subprocess.TimeoutExpired:
            return "Function execution timeout in warm container"
        except Exception as e:
            error_msg = f"Error executing in warm container: {str(e)}"
            print(error_msg)
            return error_msg
    
    def cleanup_warm(self, container_id: str) -> None:
        """Warm 컨테이너를 정리합니다."""
        try:
            subprocess.run(["docker", "rm", "-f", container_id], 
                         capture_output=True, text=True, timeout=10)
        except Exception as e:
            print(f"Error cleaning up warm container {container_id}: {e}")