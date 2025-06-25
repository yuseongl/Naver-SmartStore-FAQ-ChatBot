from core import get_logs
from fastapi import APIRouter

router = APIRouter()

@router.get("/logs")
async def get_logs_route():
    return get_logs()
