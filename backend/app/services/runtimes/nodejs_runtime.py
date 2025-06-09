import os
import subprocess
import json
from typing import Dict, Any
from .runtime_interface import RuntimeInterface

class NodejsRuntime(RuntimeInterface):

    def prepare(self, func_path: str, code: str, entrypoint: str):
        """Node.js 함수 실행을 위한 index.js 파일을 생성합니다."""
        with open(os.path.join(func_path, "index.js"), "w") as f:
            f.write(code)
    
    def run(self, func_path: str, event: Dict[str, Any]) -> str:
        """Node.js 함수를 Docker 컨테이너에서 실행합니다."""
        event_json = json.dumps(event)

        exec_script = f"""
const {{ handler }} = require('./index.js');
const event = { event_json };
(async () => {{
    const result = await handler(event);
    console.log(result);
}})();
"""

        with open(os.path.join(func_path, "run.js"), "w") as f:
            f.write(exec_script)

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath(func_path)}:/app",
            "-w", "/app",
            "node:16",
            "node", "run.js"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return result.stderr.strip()