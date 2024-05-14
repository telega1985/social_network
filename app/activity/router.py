from fastapi import APIRouter

from app.activity.schemas import SActivity
from app.activity.services import ActivityService


router_activity = APIRouter(
    prefix="/activity",
    tags=["Активные пользователи"]
)


@router_activity.get("/user/{username}")
async def get_activities_by_username(
        username: str, page: int = 1, limit: int = 10
) -> list[SActivity]:
    return await ActivityService.service_get_activities_by_username(username, page, limit)
