# Barq

A serverless function execution platform with warm container pooling.

## What is this?

Barq is a lightweight serverless platform that lets you deploy and execute Python functions in isolated Docker containers. It's built for learning serverless concepts and includes a warm pool system for better performance.

## Tech Stack

**Frontend:**
- Next.js 15 with React 19
- TypeScript
- Tailwind CSS + shadcn/ui components

**Backend:**
- FastAPI (Python)
- CouchDB for function metadata and logs
- Docker for function execution

## Quick Start with Docker Compose

### Prerequisites
- Docker & Docker Compose installed
- Git

### 🚀 One-Command Startup

1. **Clone and start everything:**
   ```bash
   git clone <repository-url>
   cd barq
   
   # Setup environment variables (first time only)
   ./setup.sh
   
   # Start all services with Docker Compose
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Access the platform:**
   - **Web UI**: http://localhost:3000
   - **API Documentation**: http://localhost:8000/docs
   - **CouchDB Admin**: http://localhost:5984/_utils (admin/admin)

### 🛠️ Development Commands

```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f

# View specific service logs
docker-compose -f docker-compose.dev.yml logs -f frontend
docker-compose -f docker-compose.dev.yml logs -f backend

# Stop all services
docker-compose -f docker-compose.dev.yml down

# Restart specific service
docker-compose -f docker-compose.dev.yml restart frontend

# Check service status
docker-compose -f docker-compose.dev.yml ps
```

### 🎯 Production Deployment

```bash
# For production use
docker-compose up -d --build
```

## Configuration

### Docker Compose Services

**CouchDB:**
- Port: 5984
- Admin credentials: admin/admin
- Data volume: `couchdb_data_dev`

**Backend (FastAPI):**
- Port: 8000
- Environment: Configured via `docker-compose.dev.yml`
- Code hot-reload: ✅ (mounted volume)

**Frontend (Next.js):**
- Port: 3000
- Environment: Development mode with hot-reload
- Node modules: Cached in anonymous volume

### Environment Variables

The `setup.sh` script creates necessary environment files:

**Backend (backend/.env):**
- `COUCHDB_URL`: CouchDB connection URL
- `ALLOWED_ORIGINS`: CORS allowed origins
- `UVICORN_HOST/PORT`: Server host and port

**Frontend (frontend/.env.local):**
- `NEXT_PUBLIC_API_URL`: Backend API URL for browser

### Docker Network

All services run on the `barq-network-dev` bridge network for secure inter-service communication.

## Current Features

- **Function Deployment**: Upload Python code with custom entrypoints
- **Dynamic Runtime Support**: Extensible runtime system (currently Python 3.10)
- **Warm Container Pool**: Pre-warmed containers for faster execution
- **Real-time Logs**: Execution logs stored in CouchDB
- **Web UI**: Modern interface for deploying and testing functions
- **Custom Events**: JSON event input for function testing
- **Auto Cleanup**: TTL-based container cleanup (5-minute default)

## How it works

1. **Deploy**: Write Python code and deploy it through the web interface
2. **Warm Pool**: System automatically creates warm containers for faster execution
3. **Execute**: Call your functions with custom JSON events
4. **Scale**: Containers are managed automatically with TTL-based cleanup

## Current Status

- ✅ **Docker Compose setup** - One-command deployment
- ✅ **Ubuntu-based containers** - Stable dependency management
- ✅ **Python runtime** with warm pools
- ✅ **Function deployment and execution**
- ✅ **Web interface** with real-time feedback
- ✅ **Container lifecycle management**
- ✅ **Execution logging and monitoring**
- ✅ **Environment variable configuration**
- ✅ **Development hot-reload** for both frontend and backend
- 🚧 Additional runtimes (Node.js, etc.)
- 🚧 Authentication/authorization
- 🚧 Resource limits and quotas

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    CouchDB      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Database)    │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5984    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Docker Network  │
                    │ barq-network-dev│
                    └─────────────────┘
```

## Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using the ports
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5984

# Stop conflicting services
docker-compose -f docker-compose.dev.yml down
```

**"Failed to fetch" errors:**
- Make sure all services are running: `docker-compose -f docker-compose.dev.yml ps`
- Check service logs: `docker-compose -f docker-compose.dev.yml logs`
- Wait for services to fully start (especially frontend npm install)

**Container build failures:**
```bash
# Clean build (removes cache)
docker-compose -f docker-compose.dev.yml build --no-cache

# Remove all containers and volumes
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f
```

**Permission issues:**
```bash
# Fix Docker socket permissions (Linux)
sudo chmod 666 /var/run/docker.sock
```

Just a fun project to explore serverless architecture patterns! 🚀
