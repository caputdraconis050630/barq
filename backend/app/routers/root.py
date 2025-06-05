from fastapi import APIRouter
from app.services.hello_service import get_greeting

router = APIRouter(prefix="", tags=["Root"])

@router.get("/")
def root():
    return {"message": get_greeting()}