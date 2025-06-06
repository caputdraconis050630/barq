# 함수 업로드 및 실행 라우터

from fastapi import APIRouter
from app.models.function_model import FunctionCreateRequest, FunctionInvokeRequest
from app.services.function_service import save_function, invoke_function

router = APIRouter(prefix="/functions", tags=["Functions"])

@router.post("/")
def create_function_route(req: FunctionCreateRequest):
    save_function(req.func_id, req.entrypoint, req.code)
    return {"status": "saved", "func_id": req.func_id}

@router.post("/{func_id}/invoke")
def invoke_function_route(func_id: str, req: FunctionInvokeRequest):
    result = invoke_function(func_id, req.event)
    return {"output": result}