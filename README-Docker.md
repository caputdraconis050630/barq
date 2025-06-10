# Barq - Docker Setup

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd barq

# Setup environment (first time only)
./setup.sh

# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Access the application
open http://localhost:3000
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js web interface |
| Backend | 8000 | FastAPI server |
| CouchDB | 5984 | Database |

## Commands

```bash
# Development (with hot reload)
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose up -d --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Clean rebuild
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
```

## Volumes

- `couchdb_data_dev`: Persistent CouchDB data
- `backend_storage_dev`: Backend storage
- `./frontend:/app`: Frontend code (hot reload)
- `./backend:/app`: Backend code (hot reload) 