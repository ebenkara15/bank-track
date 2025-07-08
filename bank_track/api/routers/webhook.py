from typing import Annotated

from fastapi import Body, Depends, HTTPException
from fastapi.routing import APIRouter

from bank_track.api.database import get_service
from bank_track.core.schemas.users import ClerkUserCreate, ClerkUserRead
from bank_track.services.crud import UserSQLService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(
    "/user",
    description="Create a new user from the payload sent by Clerk provider. The webhook must be of type `user.created`. See the doc [here](https://clerk.com/docs/webhooks/overview).",
)
async def create_user(
    data: Annotated[
        dict,
        Body(description="The payload sent by Clerk provider."),
    ],
    svc: Annotated[UserSQLService, Depends(get_service(UserSQLService))],
) -> ClerkUserRead:
    if data["type"] != "user.created":
        raise HTTPException(400, "Invalid webhook type")

    user_id = data["data"]["id"]
    user = ClerkUserCreate(user_id=user_id)
    return await svc.create(user)
