import os
import subprocess
import json
from typing import Dict, Any
from .runtime_interface import RuntimeInterface

class GoRuntime(RuntimeInterface):


    def prepare(self, func_path: str, code: str, entrypoint: str):
        with open(os.path.join(func_path, "handler.go"), "w") as f:
            f.write(code)
    
    def run(self, func_path: str, event: Dict[str, Any], log_path: str) -> str:
        event_json = json.dumps(event)

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(func_path)}:/go",
            "-w", "/go",
            "-e", f"EVENT={event_json}", # 환경변수로 이벤트 전달
            "golang:1.21",
            "go", "run", "handler.go"
        ]

        with open(log_path, "w") as log_file:
            result = subprocess.run(cmd, stdout=log_file, stderr=log_file, text=True, timeout=10)
        
        with open(log_path, "r") as log_file:
            return log_file.read()
            