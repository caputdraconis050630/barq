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
async def get_all_functions_route():
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
async def list_function_logs_route(func_id: str):
    logs = await list_logs_for_function(func_id)
    return {"logs": logs}

# 로그 파일 내용 조회
@router.get("/logs/{log_id}")
async def get_function_log_route(log_id: str):
    log = await get_log_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
