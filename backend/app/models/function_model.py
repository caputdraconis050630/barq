from pydantic import BaseModel
from typing import Any, Dict

class FunctionCreateRequest(BaseModel):
    func_id: str
    runtime: str
    entrypoint: str
    code: str

class FunctionInvokeRequest(BaseModel):
    event: Dict[str, Any]