from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Path
from fastapi.routing import APIRouter

from bank_track.api.database import get_service
from bank_track.api.page import PaginatedResponse
from bank_track.api.query import DateRangeDep, OrderingDep, PaginateDep
from bank_track.api.security import get_user_id
from bank_track.core.schemas.balances import BalanceCreate, BalanceRead, BalanceUpdate
from bank_track.services.crud import BalanceSQLService

router = APIRouter(prefix="/balances", tags=["balances"])


@router.get(
    "/",
    description="List balances that belong to the connected user through his JWT.",
)
async def get_balances(
    # date_range: Annotated[
    #     DateRangeFilter, Query(description="The date range to be used for filtering.")
    # ],
    # ordering: Annotated[
    #     OrderingFilter, Query(description="The base ordering to use for results.")
    # ],
    # paginate: Annotated[bool, Query(description="Whether to paginate response or not.")],
    date_range: DateRangeDep,
    ordering: OrderingDep,
    paginate: PaginateDep,
    user_id: Annotated[str, Depends(get_user_id)],
    svc: BalanceSQLService = Depends(get_service(BalanceSQLService)),
) -> list[BalanceRead] | PaginatedResponse[BalanceRead]:
    if not user_id:
        raise HTTPException(404, "User not found")

    return await svc.list_by(
        ordering=ordering,
        paginate=paginate,
        user_id=user_id,
        reference_date__gte=date_range.date_from,
        reference_date__lte=date_range.date_to,
    )


@router.get(
    "/account/{account_id}",
    description="List balances for the given `account_id` and that belong to the connected user through his JWT.",
)
async def get_by_account(
    account_id: Annotated[
        str,
        Path(description="The ID of the account."),
    ],
    date_range: DateRangeDep,
    ordering: OrderingDep,
    paginate: PaginateDep,
    # date_range: Annotated[
    #     DateRangeFilter, Query(description="The date range to be used for filtering.")
    # ],
    # ordering: Annotated[
    #     OrderingFilter, Query(description="The base ordering to use for results.")
    # ],
    # paginate: Annotated[
    #     bool, Query(description="Whether to paginate response or not.")
    # ],
    user_id: Annotated[str, Depends(get_user_id)],
    svc: Annotated[BalanceSQLService, Depends(get_service(BalanceSQLService))],
) -> list[BalanceRead] | PaginatedResponse[BalanceRead]:
    if not user_id:
        raise HTTPException(404, "User not found")

    return await svc.list_by(
        ordering=ordering,
        paginate=paginate,
        user_id=user_id,
        account_id=account_id,
        reference_date__gte=date_range.date_from,
        reference_date__lte=date_range.date_to,
    )


@router.post(
    "/",
    description="Create a new balance entry for the connected user through his JWT.",
)
async def create_balance(
    balance: BalanceCreate,
    user_id: Annotated[str, Depends(get_user_id)],
    svc: Annotated[BalanceSQLService, Depends(get_service(BalanceSQLService))],
) -> BalanceRead:
    if user_id:
        return await svc.create(balance)

    raise HTTPException(403, "User ID mismatch")


@router.delete(
    "/{balance_id}",
    description="Deletes a balance for the connected user through his JWT.",
)
async def delete_balance(
    balance_id: UUID,
    user_id: Annotated[str, Depends(get_user_id)],
    svc: Annotated[BalanceSQLService, Depends(get_service(BalanceSQLService))],
) -> Optional[BalanceRead]:
    if user_id:
        return await svc.delete(balance_id)

    raise HTTPException(403, "User ID mismatch")


@router.put(
    "/{balance_id}",
    description="Update a balance for the connected user through his JWT.",
)
async def update_balance(
    balance_id: UUID,
    balance: BalanceUpdate,
    user_id: Annotated[str, Depends(get_user_id)],
    svc: Annotated[BalanceSQLService, Depends(get_service(BalanceSQLService))],
) -> Optional[BalanceRead]:
    if user_id:
        return await svc.update(balance)
    raise HTTPException(403, "User ID mismatch")
