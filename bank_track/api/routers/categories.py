from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter

from bank_track.api.database import get_service
from bank_track.api.security import get_user_id
from bank_track.core.adapters import ExpenseCategorySQLService
from bank_track.core.models.categories import (
    ExpenseCategoryCreate,
    ExpenseCategoryRead,
    ExpenseCategoryUpdate,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/")
def get_categories(
    user_id: str = Depends(get_user_id),
    svc: ExpenseCategorySQLService = Depends(get_service(ExpenseCategorySQLService)),
) -> list[ExpenseCategoryRead]:
    return svc.list_by(user_id=user_id)


@router.post("/")
def create_category(
    category: ExpenseCategoryCreate,
    user_id: str = Depends(get_user_id),
    svc: ExpenseCategorySQLService = Depends(get_service(ExpenseCategorySQLService)),
) -> ExpenseCategoryRead:
    category.user_id = user_id

    return svc.create(category)


@router.delete("/{category_id}")
def delete_category(
    category_id: UUID,
    user_id: str = Depends(get_user_id),
    svc: ExpenseCategorySQLService = Depends(get_service(ExpenseCategorySQLService)),
) -> Optional[ExpenseCategoryRead]:
    user_category = svc.get(category_id)
    if not user_category:
        raise HTTPException(404, "Categories not found")
    if user_category.user_id != user_id:
        raise HTTPException(403, "User ID mismatch")

    return svc.delete(category_id)


@router.put("/{category_id}")
def update_category(
    category_id: UUID,
    category: ExpenseCategoryUpdate,
    user_id: str = Depends(get_user_id),
    svc: ExpenseCategorySQLService = Depends(get_service(ExpenseCategorySQLService)),
) -> Optional[ExpenseCategoryRead]:
    user_category = svc.get(category_id)
    if not user_category:
        raise HTTPException(404, "Categories not found")
    if user_category.user_id != user_id:
        raise HTTPException(403, "User ID mismatch")
    return svc.update(category)
