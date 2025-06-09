#!/bin/bash

# 환경변수 파일이 있으면 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

# 기본값 설정
export UVICORN_HOST=${UVICORN_HOST:-0.0.0.0}
export UVICORN_PORT=${UVICORN_PORT:-8000}

# 포트를 사용 중인 프로세스 확인 및 종료
echo "Checking for existing processes on port ${UVICORN_PORT}..."
EXISTING_PID=$(lsof -t -i:${UVICORN_PORT} 2>/dev/null)

if [ ! -z "$EXISTING_PID" ]; then
    echo "Found process(es) using port ${UVICORN_PORT}: $EXISTING_PID"
    echo "Terminating existing process(es)..."
    
    # SIGTERM으로 우아하게 종료 시도
    kill $EXISTING_PID 2>/dev/null
    
    # 3초 대기 후 프로세스가 여전히 실행 중이면 강제 종료
    sleep 3
    STILL_RUNNING=$(lsof -t -i:${UVICORN_PORT} 2>/dev/null)
    if [ ! -z "$STILL_RUNNING" ]; then
        echo "Force killing process(es)..."
        kill -9 $STILL_RUNNING 2>/dev/null
        sleep 1
    fi
    
    echo "Existing process(es) terminated."
else
    echo "No existing process found on port ${UVICORN_PORT}."
fi

echo "Starting server on ${UVICORN_HOST}:${UVICORN_PORT}..."
uvicorn app.main:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --reload
