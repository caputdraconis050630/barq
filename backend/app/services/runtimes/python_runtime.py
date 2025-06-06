import os
import subprocess
from typing import Dict, Any
from .runtime_interface import RuntimeInterface

class PythonRuntime(RuntimeInterface):

    def prepare(self, func_path: str, code: str, entrypoint: str):
        with open(os.path.join(func_path, "handler.py"), "w") as f:
            f.write(code)
    
    def run(self, func_path: str, event: Dict[str, Any], log_path: str) -> str:
        exec_script = f"""
import json
from handler import main
from event import event
result = main(event)
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

    with open(log_path, "w") as log_file:
        result = subprocess.run(cmd, stdout=log_file, stderr=log_file, text=True,timeout=10)
    
    with open(log_path, "r") as log_file:
        return log_file.read()