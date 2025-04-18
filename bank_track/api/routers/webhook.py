from typing import Annotated

from fastapi import Body, Depends, HTTPException
from fastapi.routing import APIRouter

from bank_track.api.database import get_service
from bank_track.core.adapters import UserSQLService
from bank_track.core.models.users import ClerkUserCreate, ClerkUserRead

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(
    "/user",
    description="Create a new user from the payload sent by Clerk provider. The webhook must be of type `user.created`. See the doc [here](https://clerk.com/docs/webhooks/overview).",
)
def create_user(
    data: Annotated[
        dict,
        Body(description="The payload sent by Clerk provider."),
    ],
    svc: UserSQLService = Depends(get_service(UserSQLService)),
) -> ClerkUserRead:
    if data["type"] != "user.created":
        raise HTTPException(400, "Invalid webhook type")

    user_id = data["data"]["id"]
    user = ClerkUserCreate(user_id=user_id)
    return svc.create(user)
