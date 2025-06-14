import httpx
from datetime import datetime
from app.models.function_model import FunctionCreateRequest
import os

COUCHDB_URL = os.getenv("COUCHDB_URL")
FUNCTION_DB_NAME = os.getenv("FUNCTION_DB_NAME")

async def create_database_if_not_exists():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{COUCHDB_URL}/{FUNCTION_DB_NAME}") # 데이터베이스 조회
        if r.status_code == 404:
            await client.put(f"{COUCHDB_URL}/{FUNCTION_DB_NAME}") # 데이터베이스 생성

async def create_function_document(req: FunctionCreateRequest):
    await create_database_if_not_exists()

    doc = {
        "_id": req.func_id,
        "runtime": req.runtime,
        "entrypoint": req.entrypoint,
        "code": req.code,
        "created_at": datetime.now().isoformat(),
    }

    async with httpx.AsyncClient() as client:
        r = await client.put(f"{COUCHDB_URL}/{FUNCTION_DB_NAME}/{req.func_id}", json=doc)
        if r.status_code == 409:
            raise ValueError(f"Function document already exists: {req.func_id}")
        elif r.status_code >= 400:
            raise RuntimeError(f"CouchDB Error: {r.text}")
    
async def list_functions():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{COUCHDB_URL}/{FUNCTION_DB_NAME}/_all_docs?include_docs=true")
        docs = r.json().get("rows", [])
        return [doc["doc"] for doc in docs]

async def get_function_metadata(func_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{COUCHDB_URL}/{FUNCTION_DB_NAME}/{func_id}")
        if r.status_code == 404:
            return None
        elif r.status_code >= 400:
            raise RuntimeError(f"CouchDB Error: {r.text}")
        return r.json()
        