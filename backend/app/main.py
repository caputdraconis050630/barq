# fastAPI Entrypoint

from fastapi import FastAPI
from app.routers import root, functions
from app.core.exception_handler import add_exception_handler

app = FastAPI(title="Barq API")

# 라우터 등록
app.include_router(root.router)
app.include_router(functions.router)

# 예외 처리 핸들러 등록
add_exception_handler(app)
