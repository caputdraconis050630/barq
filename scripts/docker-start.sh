#!/bin/bash

echo "🚀 Starting Barq production stack..."

# 기존 컨테이너 정리 (선택적)
echo "Stopping existing containers..."
docker-compose down

# 이미지 빌드 및 컨테이너 시작
echo "Building and starting containers..."
docker-compose up --build -d

echo "✅ Barq stack started successfully!"
echo ""
echo "🌐 Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - CouchDB: http://localhost:5984"
echo ""
echo "📊 Check status: docker-compose ps"
echo "📝 View logs: docker-compose logs -f [service_name]"
echo "🛑 Stop services: docker-compose down" 