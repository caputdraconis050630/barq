#!/bin/bash

echo "🛠️ Starting Barq development stack..."

# 기존 컨테이너 정리 (선택적)
echo "Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down

# 이미지 빌드 및 컨테이너 시작
echo "Building and starting development containers..."
docker-compose -f docker-compose.dev.yml up --build -d

echo "✅ Barq development stack started successfully!"
echo ""
echo "🌐 Services:"
echo "  - Frontend (dev): http://localhost:3000"
echo "  - Backend API (dev): http://localhost:8000"
echo "  - CouchDB: http://localhost:5984"
echo ""
echo "📊 Check status: docker-compose -f docker-compose.dev.yml ps"
echo "📝 View logs: docker-compose -f docker-compose.dev.yml logs -f [service_name]"
echo "🛑 Stop services: docker-compose -f docker-compose.dev.yml down"
echo ""
echo "💡 Development mode features:"
echo "  - Hot reload enabled for both frontend and backend"
echo "  - Code changes will be reflected automatically" 