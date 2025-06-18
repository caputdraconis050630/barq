#!/bin/bash

# 개발 서버 포트 설정
DEV_PORT=${PORT:-3000}

# 포트를 사용 중인 프로세스 확인 및 종료
echo "Checking for existing processes on port ${DEV_PORT}..."
EXISTING_PID=$(lsof -t -i:${DEV_PORT} 2>/dev/null)

if [ ! -z "$EXISTING_PID" ]; then
    echo "Found process(es) using port ${DEV_PORT}: $EXISTING_PID"
    echo "Terminating existing process(es)..."
    
    # SIGTERM으로 우아하게 종료 시도
    kill $EXISTING_PID 2>/dev/null
    
    # 3초 대기 후 프로세스가 여전히 실행 중이면 강제 종료
    sleep 3
    STILL_RUNNING=$(lsof -t -i:${DEV_PORT} 2>/dev/null)
    if [ ! -z "$STILL_RUNNING" ]; then
        echo "Force killing process(es)..."
        kill -9 $STILL_RUNNING 2>/dev/null
        sleep 1
    fi
    
    echo "Existing process(es) terminated."
else
    echo "No existing process found on port ${DEV_PORT}."
fi

echo "Starting development server on port ${DEV_PORT}..."
npm run dev 