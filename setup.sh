#!/bin/bash

echo "Setting up Barq environment..."

# 백엔드 환경변수 설정
if [ ! -f backend/.env ]; then
    echo "Creating backend/.env from template..."
    cp backend/env.template backend/.env
    echo "✅ Backend .env file created"
else
    echo "⚠️  Backend .env file already exists"
fi

# 프론트엔드 환경변수 설정
if [ ! -f frontend/.env.local ]; then
    echo "Creating frontend/.env.local from template..."
    cp frontend/env.template frontend/.env.local
    echo "✅ Frontend .env.local file created"
else
    echo "⚠️  Frontend .env.local file already exists"
fi

echo ""
echo "🔧 Environment setup completed!"
echo ""
echo "Please review and modify the following files as needed:"
echo "  - backend/.env (CouchDB, server settings)"
echo "  - frontend/.env.local (API URL)"
echo ""
echo "To start the services:"
echo "  1. Start CouchDB: cd database && ./up.sh"
echo "  2. Start Backend: cd backend && ./scripts/start_server.sh"
echo "  3. Start Frontend: cd frontend && npm run dev" 