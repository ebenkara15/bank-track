from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter

from bank_track.api.database import get_service
from bank_track.api.page import PaginatedResponse
from bank_track.api.security import get_user_id
from bank_track.core.schemas.categories import (
    ExpenseCategoryCreate,
    ExpenseCategoryRead,
    ExpenseCategoryUpdate,
)
from bank_track.services.crud import ExpenseCategorySQLService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "/",
    description="List categories that belong to the connected user through his JWT.",
)
async def get_categories(
    user_id: Annotated[str, Depends(get_user_id)],
    svc: Annotated[
        ExpenseCategorySQLService, Depends(get_service(ExpenseCategorySQLService))
    ],
) -> list[ExpenseCategoryRead] | PaginatedResponse[ExpenseCategoryRead]:
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    return await svc.list_by(paginate=False, user_id=user_id)


@router.post(
    "/",
    description="Create a new category for the connected user.",
)
async def create_category(
    category: ExpenseCategoryCreate,
    user_id: Annotated[str, Depends(get_user_id)],
    svc: Annotated[
        ExpenseCategorySQLService, Depends(get_service(ExpenseCategorySQLService))
    ],
) -> ExpenseCategoryRead:
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    category.user_id = user_id
    return await svc.create(category)


@router.delete(
    "/{category_id}",
    description="Deletes a category given the `category_id` for the connected user.",
)
async def delete_category(
    category_id: UUID,
    user_id: Annotated[str, Depends(get_user_id)],
    svc: Annotated[
        ExpenseCategorySQLService, Depends(get_service(ExpenseCategorySQLService))
    ],
) -> Optional[ExpenseCategoryRead]:
    user_category = await svc.get(category_id)
    if not user_category:
        raise HTTPException(404, "Categories not found")
    if user_category.user_id != user_id:
        raise HTTPException(403, "User ID mismatch")

    return await svc.delete(category_id)


@router.put(
    "/{category_id}",
    description="Updates the categy given the `category_id` for the connected user.",
)
async def update_category(
    category_id: UUID,
    category: ExpenseCategoryUpdate,
    user_id: Annotated[str, Depends(get_user_id)],
    svc: Annotated[
        ExpenseCategorySQLService, Depends(get_service(ExpenseCategorySQLService))
    ],
) -> Optional[ExpenseCategoryRead]:
    user_category = await svc.get(category_id)
    if not user_category:
        raise HTTPException(404, "Category not found")
    if user_category.user_id != user_id:
        raise HTTPException(403, "User ID mismatch")
    return await svc.update(category)
