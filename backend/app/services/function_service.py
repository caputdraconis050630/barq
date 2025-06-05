import os
import subprocess
import yaml
import uuid
from typing import Any, Dict

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage") # /backend/storage

def save_function(func_id: str, entrypoint: str, code: str):
    # 함수 저장 경로 생성
    func_path = os.path.join(BASE_DIR, func_id)
    os.makedirs(func_path, exist_ok=True)

    # 함수 코드 저장
    handler_path = os.path.join(func_path, "handler.py") # 일단은? 파이썬만
    with open(handler_path, "w") as f:
        f.write(code)

    # function.yaml로 메타데이터 저장
    meta_path = os.path.join(func_path, "function.yaml")
    with open(meta_path, "w") as f:
        yaml.dump({
            "entrypoint": entrypoint,
            "runtime": "python3.10",
            "handler": "handler.handler",
        }, f)

def invoke_function(func_id: str, event: Dict[str, Any]):
    func_path = os.path.join(BASE_DIR, func_id)
    handler_path = os.path.join(func_path, "handler.py")
    event_path = os.path.join(func_path, "event.json")
    meta_path = os.path.join(func_path, "function.yaml")

    with open(meta_path, "r") as f:
        meta = yaml.safe_load(f)

    runtime = meta.get("runtime", "python3.10")
    handler = meta.get("handler", "handler.handler")

    with open(event_path, "w") as f:
        f.write("event = " + str(event))

    # 실행 스크립트
    exec_script = f"""
import json
from handler import main
from event import event
result = main(event)
print(result)
"""
    exec_path = os.path.join(func_path, "run.py")
    with open(exec_path, "w") as f:
        f.write(exec_script)

    # Docker 컨테이너 실행
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(func_path)}:/app", # 컨테이너 내부에서 함수 코드 접근 가능하도록
        "-w", "/app", # 작업 디렉토리 설정
        "python:3.10",
        "python", "run.py"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return f"Error: {result.stderr.strip()}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: Function execution timed out"

