import httpx
import os
from datetime import datetime
from typing import Dict, Any

COUCHDB_URL = os.getenv("COUCHDB_URL")
LOG_DB_NAME = os.getenv("LOG_DB_NAME")

async def create_log_db_if_not_exists():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{COUCHDB_URL}/{LOG_DB_NAME}")
        if r.status_code == 404:
            await client.put(f"{COUCHDB_URL}/{LOG_DB_NAME}")

async def save_execution_log(func_id: str, output:str, success: bool, event: Dict[str, Any]):
    await create_log_db_if_not_exists()
    timestamp = datetime.utcnow().isoformat()
    log_id = f"log-{func_id}-{timestamp}"

    doc = {
        "_id": log_id,
        "func_id": func_id,
        "timestamp": timestamp,
        "output": output,
        "event": event,
        "success": success,
    }

    async with httpx.AsyncClient() as client:
        r = await client.put(f"{COUCHDB_URL}/{LOG_DB_NAME}/{log_id}", json=doc)
        if r.status_code >= 400:
            raise RuntimeError(f"Failed to save log: {r.text}")
    
async def list_logs_for_function(func_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{COUCHDB_URL}/{LOG_DB_NAME}/_all_docs?include_docs=true")
        docs = r.json().get("rows", [])
        return [
            doc["doc"] for doc in docs
            if doc["doc"].get("func_id") == func_id
        ]

async def get_log_by_id(log_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{COUCHDB_URL}/{LOG_DB_NAME}/{log_id}")
        if r.status_code == 404:
            raise ValueError(f"Log {log_id} not found")
        return r.json()
    

            
            