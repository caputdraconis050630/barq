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

## Quick Start

1. **Setup environment variables:**
   ```bash
   ./setup.sh
   ```

2. **Start services:**
   ```bash
   # Start CouchDB
   cd database && ./up.sh
   
   # Start Backend (in new terminal)
   cd backend && ./scripts/start_server.sh
   
   # Start Frontend (in new terminal)
   cd frontend && npm install && npm run dev
   ```

3. **Access the platform:**
   - Web UI: http://localhost:3000
   - API: http://localhost:8000

## Configuration

**Backend (backend/.env):**
- `COUCHDB_URL`: CouchDB connection URL
- `ALLOWED_ORIGINS`: CORS allowed origins
- `UVICORN_HOST/PORT`: Server host and port

**Frontend (frontend/.env.local):**
- `NEXT_PUBLIC_API_URL`: Backend API URL

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

- ✅ Python runtime with warm pools
- ✅ Function deployment and execution
- ✅ Web interface with real-time feedback
- ✅ Container lifecycle management
- ✅ Execution logging and monitoring
- ✅ Environment variable configuration
- 🚧 Additional runtimes (Node.js, etc.)
- 🚧 Authentication/authorization
- 🚧 Resource limits and quotas

Just a fun project to explore serverless architecture patterns!
