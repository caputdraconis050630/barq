# 함수 업로드 및 실행 라우터

import os
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi import Request
from app.models.function_model import FunctionCreateRequest, FunctionInvokeRequest
from app.services.function_service import save_function, invoke_function, get_warm_pool_stats
from app.registry.couchdb_registry import create_function_document, list_functions, get_function_metadata
from app.registry.log_registry import list_logs_for_function, get_log_by_id

router = APIRouter(prefix="", tags=["Root"])

# root 라우터
@router.get("/")
def root_router():
    return {
        "message": "Welcome to Barq API"
    }
