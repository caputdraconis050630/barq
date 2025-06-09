import httpx
import os
from datetime import datetime
from typing import Dict, Any, Optional

COUCHDB_URL = os.getenv("COUCHDB_URL")
LOG_DB_NAME = os.getenv("LOG_DB_NAME")

async def create_log_db_if_not_exists():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{COUCHDB_URL}/{LOG_DB_NAME}")
        if r.status_code == 404:
            await client.put(f"{COUCHDB_URL}/{LOG_DB_NAME}")

async def save_execution_log(
    func_id: str, 
    output: str, 
    success: bool, 
    event: Dict[str, Any],
    execution_type: str = "cold",  # "cold", "warm", "reused"
    coldstart_time_ms: Optional[float] = None,
    execution_time_ms: Optional[float] = None,
    total_time_ms: Optional[float] = None,
    container_id: Optional[str] = None
):
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
        "performance": {
            "execution_type": execution_type,
            "coldstart_time_ms": coldstart_time_ms,
            "execution_time_ms": execution_time_ms,
            "total_time_ms": total_time_ms
        },
        "container_id": container_id
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

async def get_performance_stats(func_id: str):
    """함수의 성능 통계를 반환합니다."""
    logs = await list_logs_for_function(func_id)
    
    cold_starts = []
    warm_starts = []
    execution_times = []
    
    for log in logs:
        perf = log.get("performance", {})
        if perf.get("execution_type") == "cold" and perf.get("coldstart_time_ms"):
            cold_starts.append(perf["coldstart_time_ms"])
        elif perf.get("execution_type") == "warm":
            warm_starts.append(perf.get("execution_time_ms", 0))
        
        if perf.get("execution_time_ms"):
            execution_times.append(perf["execution_time_ms"])
    
    stats = {
        "function_id": func_id,
        "total_invocations": len(logs),
        "cold_start_count": len(cold_starts),
        "warm_start_count": len(warm_starts),
        "avg_coldstart_ms": sum(cold_starts) / len(cold_starts) if cold_starts else 0,
        "avg_warmstart_ms": sum(warm_starts) / len(warm_starts) if warm_starts else 0,
        "avg_execution_ms": sum(execution_times) / len(execution_times) if execution_times else 0,
        "min_coldstart_ms": min(cold_starts) if cold_starts else 0,
        "max_coldstart_ms": max(cold_starts) if cold_starts else 0,
    }
    
    return stats
    

            
            