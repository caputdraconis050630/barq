#!/bin/bash

# 환경변수 파일이 있으면 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

# 기본값 설정
export UVICORN_HOST=${UVICORN_HOST:-0.0.0.0}
export UVICORN_PORT=${UVICORN_PORT:-8000}

echo "Starting server on ${UVICORN_HOST}:${UVICORN_PORT}..."
uvicorn app.main:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --reload
