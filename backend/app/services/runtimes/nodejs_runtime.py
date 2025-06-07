import os
import subprocess
import json
from typing import Dict, Any
from .runtime_interface import RuntimeInterface

class NodejsRuntime(RuntimeInterface):

    def prepare(self, func_path: str, code: str, entrypoint: str):
        with open(os.path.join(func_path, "index.js"), "w") as f:
            f.write(code)
    
    def run(self, func_path: str, event: Dict[str, Any], log_path: str) -> str:
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

        with open(log_path, "w") as log_file:
            result = subprocess.run(cmd, stdout=log_file, stderr=log_file, text=True, timeout=10)
        
        with open(log_path, "r") as log_file:
            return log_file.read()