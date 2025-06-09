import os
import subprocess
import json
from typing import Dict, Any
from .runtime_interface import RuntimeInterface

class GoRuntime(RuntimeInterface):

    def prepare(self, func_path: str, code: str, entrypoint: str):
        """Go 함수 실행을 위한 handler.go 파일을 생성합니다."""
        with open(os.path.join(func_path, "handler.go"), "w") as f:
            f.write(code)
    
    def run(self, func_path: str, event: Dict[str, Any]) -> str:
        """Go 함수를 Docker 컨테이너에서 실행합니다."""
        event_json = json.dumps(event)

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(func_path)}:/go",
            "-w", "/go",
            "-e", f"EVENT={event_json}", # 환경변수로 이벤트 전달
            "golang:1.21",
            "go", "run", "handler.go"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return result.stderr.strip()
            