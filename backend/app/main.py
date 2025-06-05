# fastAPI Entrypoint

from fastapi import FastAPI
from app.routers import root
from app.core.exception_handler import add_exception_handlers

app = FastAPI(title="Serverless Platform - Backend")

# 라우터 등록
app.include_router(root.router)

# 예외 처리 핸들러 등록
add_exception_handlers(app)
