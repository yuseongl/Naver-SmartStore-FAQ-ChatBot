from containers import Container
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/logs")
@inject
async def get_logs_route(
    logger=Depends(Provide[Container.logger]),
):
    return logger.get_logs()
