# fastAPI Entrypoint

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import functions, root
from app.core.exception_handler import add_exception_handler

app = FastAPI(title="Barq API")

# 환경변수에서 허용할 오리진 가져오기
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# CORS 미들웨어 설정 - 프론트엔드에서 API 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(functions.router)
app.include_router(root.router)

# 예외 처리 핸들러 등록
add_exception_handler(app)
