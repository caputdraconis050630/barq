# fastAPI Entrypoint

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import root, functions
from app.core.exception_handler import add_exception_handler

app = FastAPI(title="Barq API")

# CORS 미들웨어 설정 - 프론트엔드에서 API 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(root.router)
app.include_router(functions.router)

# 예외 처리 핸들러 등록
add_exception_handler(app)
