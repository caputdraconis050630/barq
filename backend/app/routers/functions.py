# 함수 업로드 및 실행 라우터

import os
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi import Request
from app.models.function_model import FunctionCreateRequest, FunctionInvokeRequest
from app.services.function_service import save_function, invoke_function
from app.registry.couchdb_registry import create_function_document, list_functions, get_function_metadata

router = APIRouter(prefix="/functions", tags=["Functions"])

# 함수 생성
@router.post("/")
async def create_function_route(req: FunctionCreateRequest):
    try:
        await create_function_document(req)
        save_function(req.func_id, req.runtime, req.entrypoint, req.code)
        return {"status": "created", "func_id": req.func_id}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 함수 실행
@router.post("/{func_id}/invoke")
def invoke_function_route(func_id: str, req: FunctionInvokeRequest):
    result = invoke_function(func_id, req.event)
    return {"output": result}

# 함수 목록 조회
@router.get("/list")
async def get_all_functions():
    try:
        functions = await list_functions()
        return {"functions": functions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 함수 메타데이터 조회
@router.get("/{func_id}")
async def get_function_metadata_route(func_id: str):
    try:
        meta = await get_function_metadata(func_id)
        return meta
    except ValueError as e:
        raise HTTPException(status_code=500, detail="Function not found")
        
# 로그 목록 조회
@router.get("/{func_id}/logs")
def list_function_logs(func_id: str):
    logs_dir = os.path.join("app", "storage", func_id, "logs")
    logs_path = os.path.abspath(logs_dir)

    if not os.path.exists(logs_path):
        raise HTTPException(status_code=404, detail="Logs not found")

    logs = sorted([
        f for f in os.listdir(logs_path)
        if os.path.isfile(os.path.join(logs_path, f)) and f.endswith(".log")
    ])

    return {"logs": logs}

# 로그 파일 내용 조회
@router.get("/{func_id}/logs/{timestamp}")
def get_function_log(func_id: str, timestamp: str):
    log_file_path = os.path.join("app", "storage", func_id, "logs", f"{timestamp}.log")
    abs_path = os.path.abspath(log_file_path)

    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="Log file not found")

    with open(abs_path, "r") as f:
        content = f.read()

    return {"timestamp": timestamp, "content": content}
