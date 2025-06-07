import os
import yaml
import uuid
from datetime import datetime
from typing import Any, Dict
from app.services.runtimes import get_runtime_handler

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage") # /backend/storage

def save_function(func_id: str, runtime: str, entrypoint: str, code: str):
    # 함수 저장 경로 생성
    func_path = os.path.join(BASE_DIR, func_id)
    os.makedirs(func_path, exist_ok=True)

    # 코드 저장
    runtime_handler = get_runtime_handler(runtime)
    runtime_handler.prepare(func_path, code, entrypoint)

    # function.yaml로 메타데이터 저장
    meta_path = os.path.join(func_path, "function.yaml")
    with open(meta_path, "w") as f:
        yaml.dump({
            "entrypoint": entrypoint,
            "runtime": runtime,
            "handler": "handler.handler",
        }, f)

def invoke_function(func_id: str, event: Dict[str, Any]):
    func_path = os.path.join(BASE_DIR, func_id)
    meta_path = os.path.join(func_path, "function.yaml")

    # Log 저장
    logs_path = os.path.join(func_path, "logs")
    os.makedirs(logs_path, exist_ok=True) # 로그 폴더 생성
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    log_file_path = os.path.join(logs_path, f"{timestamp}.log")


    with open(meta_path, "r") as f:
        meta = yaml.safe_load(f)

    runtime = meta.get("runtime", "python3.10")
    handler = meta.get("entrypoint", "handler.main")

    runtime_handler = get_runtime_handler(runtime)
    result = runtime_handler.run(func_path, event, log_file_path)

    return result

