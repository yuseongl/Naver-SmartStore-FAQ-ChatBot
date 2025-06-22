from fastapi import APIRouter
from services import get_logs

router = APIRouter()

@router.get("/logs")
async def get_logs_route():
    return get_logs()