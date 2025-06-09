# 함수 업로드 및 실행 라우터

import os
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi import Request
from app.models.function_model import FunctionCreateRequest, FunctionInvokeRequest
from app.services.function_service import save_function, invoke_function, get_warm_pool_stats, get_function_performance_stats
from app.registry.couchdb_registry import create_function_document, list_functions, get_function_metadata
from app.registry.log_registry import list_logs_for_function, get_log_by_id

router = APIRouter(prefix="/functions", tags=["Functions"])

# 런타임 목록 (가장 먼저 정의 - 경로 충돌 방지)
@router.get("/runtimes")
def get_supported_runtimes():
    """지원되는 런타임 목록을 반환합니다."""
    supported_runtimes = [
        {
            "value": "python3.12",
            "label": "Python 3.12",
            "category": "python"
        },
        {
            "value": "python3.11", 
            "label": "Python 3.11",
            "category": "python"
        },
        {
            "value": "python3.10",
            "label": "Python 3.10", 
            "category": "python"
        },
        {
            "value": "nodejs22.x",
            "label": "Node.js 22.x",
            "category": "nodejs"
        },
        {
            "value": "nodejs20.x", 
            "label": "Node.js 20.x",
            "category": "nodejs"
        },
        {
            "value": "nodejs18.x",
            "label": "Node.js 18.x",
            "category": "nodejs"
        },
        {
            "value": "go1.x",
            "label": "Go 1.x",
            "category": "go"
        }
    ]
    
    return {
        "runtimes": supported_runtimes,
        "default": "python3.11"
    }

# Warm Pool 상태 조회
@router.get("/warm-pool/stats")
def get_warm_pool_stats_route():
    """현재 warm pool의 상태를 조회합니다."""
    try:
        stats = get_warm_pool_stats()
        return {"warm_pool": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 함수 목록 조회
@router.get("/list")
async def get_all_functions_route():
    try:
        functions = await list_functions()
        return {"functions": functions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 함수 생성
@router.post("/")
async def create_function_route(req: FunctionCreateRequest):
    try:
        await save_function(req)
        return {"status": "created", "func_id": req.func_id}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 로그 파일 내용 조회
@router.get("/logs/{log_id}")
async def get_function_log_route(log_id: str):
    try:
        log = await get_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        return log
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 함수 실행
@router.post("/{func_id}/invoke")
def invoke_function_route(func_id: str, req: FunctionInvokeRequest):
    """함수를 실행하고 결과와 성능 메트릭을 반환합니다."""
    try:
        result = invoke_function(func_id, req.event)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 함수 성능 통계 조회
@router.get("/{func_id}/stats")
def get_function_stats_route(func_id: str):
    """함수의 성능 통계를 조회합니다."""
    try:
        stats = get_function_performance_stats(func_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 로그 목록 조회
@router.get("/{func_id}/logs")
async def list_function_logs_route(func_id: str):
    try:
        logs = await list_logs_for_function(func_id)
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 함수 메타데이터 조회 (가장 마지막에 정의 - 다른 경로와 충돌 방지)
@router.get("/{func_id}")
async def get_function_metadata_route(func_id: str):
    try:
        meta = await get_function_metadata(func_id)
        if not meta:
            raise HTTPException(status_code=404, detail="Function not found")
        return meta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
