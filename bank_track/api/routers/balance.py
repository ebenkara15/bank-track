from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter

from bank_track.api.database import get_service
from bank_track.api.security import get_user_id
from bank_track.core.adapters import AccountSQLService, BalanceSQLService
from bank_track.core.models.balances import BalanceCreate, BalanceRead, BalanceUpdate
from bank_track.core.models.sql import BalanceSQL

router = APIRouter(prefix="/balances", tags=["balances"])


@router.get("/")
def get_balances(
    user_id: str = Depends(get_user_id),
    svc: BalanceSQLService = Depends(get_service(BalanceSQLService)),
) -> Optional[list[BalanceRead]]:
    if user_id:
        return svc.list_by(order_by=BalanceSQL.reference_date, user_id=user_id)

    raise HTTPException(404, "User not found")


@router.get("/account/{account_id}")
def get_by_account(
    account_id: str,
    user_id: str = Depends(get_user_id),
    svc: BalanceSQLService = Depends(get_service(BalanceSQLService)),
    account_svc: AccountSQLService = Depends(get_service(AccountSQLService)),
) -> list[BalanceRead]:
    if user_id:
        return svc.list_by(user_id=user_id, account_id=account_id)

    raise HTTPException(404, "User not found")


@router.post("/")
def create_balance(
    balance: BalanceCreate,
    user_id: str = Depends(get_user_id),
    svc: BalanceSQLService = Depends(get_service(BalanceSQLService)),
) -> BalanceRead:
    if user_id:
        return svc.create(balance)

    raise HTTPException(403, "User ID mismatch")


@router.delete("/{balance_id}")
def delete_balance(
    balance_id: UUID,
    user_id: str = Depends(get_user_id),
    svc: BalanceSQLService = Depends(get_service(BalanceSQLService)),
) -> Optional[BalanceRead]:
    if user_id:
        return svc.delete(balance_id)

    raise HTTPException(403, "User ID mismatch")


@router.put("/{balance_id}")
def update_balance(
    balance_id: UUID,
    balance: BalanceUpdate,
    user_id: str = Depends(get_user_id),
    svc: BalanceSQLService = Depends(get_service(BalanceSQLService)),
    account_svc: AccountSQLService = Depends(get_service(AccountSQLService)),
) -> Optional[BalanceRead]:
    if user_id:
        return svc.update(balance)
    raise HTTPException(403, "User ID mismatch")
