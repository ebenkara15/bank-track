from typing import Annotated, Optional
from uuid import UUID

from fastapi import Body, Depends, Path, Query
from fastapi.routing import APIRouter

from bank_track.api.database import get_service
from bank_track.api.page import PaginatedResponse
from bank_track.api.query import DateRangeDep, OrderingDep, PaginateDep
from bank_track.api.security import check_ownership, get_user_id
from bank_track.core.schemas.transactions import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from bank_track.services.crud import ExpenseCategorySQLService, TransactionSQLService

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.get(
    "/{transaction_id}",
    description="Get a transaction by its ID. The transaction must belong to the connected user through his JWT.",
)
async def get_transaction(
    transaction_id: Annotated[
        UUID, Path(description="The ID of the transaction. Must be a UUID.")
    ],
    user_id: Annotated[str, Depends(get_user_id)],
    svc: Annotated[TransactionSQLService, Depends(get_service(TransactionSQLService))],
) -> Optional[TransactionRead]:
    return await svc.get_by(user_id=user_id, transaction_id=transaction_id)


@router.get(
    "/",
    description="List transactions that belong to the connected user through his JWT.",
)
async def get_all_transactions(
    date_range: DateRangeDep,
    ordering: OrderingDep,
    paginate: PaginateDep,
    svc: Annotated[TransactionSQLService, Depends(get_service(TransactionSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[TransactionRead] | PaginatedResponse[TransactionRead]:
    return await svc.list_by(
        ordering=ordering,
        paginate=paginate,
        user_id=user_id,
        value_date__gte=date_range.date_from,
        value_date__lte=date_range.date_to,
    )


@router.get(
    "/accounts/{account_id}",
    description="List all transactions for the given `account_id` and that belong to the connected user through his JWT.",
)
async def list_transactions_by_account(
    account_id: Annotated[str, Path(description="The ID of the account.")],
    date_range: DateRangeDep,
    ordering: OrderingDep,
    paginate: PaginateDep,
    svc: Annotated[TransactionSQLService, Depends(get_service(TransactionSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[TransactionRead] | PaginatedResponse[TransactionRead]:
    return await svc.list_by(
        ordering=ordering,
        paginate=paginate,
        account_id=account_id,
        user_id=user_id,
        value_date__gte=date_range.date_from,
        value_date__lte=date_range.date_to,
    )


@router.get(
    "/accounts/f/",
    description="List all transactions for the given list of account ID for the connected user through his JWT.",
)
async def list_transactions_by_accounts(
    date_range: DateRangeDep,
    ordering: OrderingDep,
    paginate: PaginateDep,
    account_ids: Annotated[
        list[str],
        Query(description="The account IDs from which to retrieve the transactions"),
    ],
    svc: Annotated[TransactionSQLService, Depends(get_service(TransactionSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[TransactionRead] | PaginatedResponse[TransactionRead]:
    return await svc.list_by(
        ordering=ordering,
        paginate=paginate,
        user_id=user_id,
        account_id=account_ids,
        value_date__gte=date_range.date_from,
        value_date__lte=date_range.date_to,
    )


@router.post(
    "/",
    description="Create a transaction for the connected user through his JWT.",
)
async def create_transaction(
    transaction: Annotated[
        TransactionCreate, Body(description="The transaction to create.")
    ],
    svc: Annotated[TransactionSQLService, Depends(get_service(TransactionSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
) -> TransactionRead:
    transaction.user_id = user_id
    return await svc.create(transaction)


@router.put(
    "/",
    description="Update a transaction for the connected user through his JWT.",
)
async def update_transaction(
    transaction: Annotated[
        TransactionUpdate,
        Body(
            description="The updated transaction. The previous transaction is identified by the `TransactionUpdate.transaction_id` field."
        ),
    ],
    svc: Annotated[TransactionSQLService, Depends(get_service(TransactionSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
) -> Optional[TransactionRead]:
    transaction.user_id = user_id
    await check_ownership(
        svc=svc,
        resource_id=transaction.id,
        user_id=user_id,
        account_id=transaction.account_id,
    )
    return await svc.update(transaction)


@router.put(
    "/{transaction_id}/classify",
    description="Classify the transaction identified by its `transaction_id` with the given categories identified by the `category_ids` list.",
)
async def update_transaction_categories(
    transaction_id: Annotated[
        UUID,
        Path(description="The ID of the transaction to classify. Must be a `UUID`."),
    ],
    category_ids: Annotated[
        list[UUID],
        Body(
            description="The list of IDs of the categories to be associated to the `transaction_id`."
        ),
    ],
    svc: Annotated[TransactionSQLService, Depends(get_service(TransactionSQLService))],
    category_svc: Annotated[
        ExpenseCategorySQLService, Depends(get_service(ExpenseCategorySQLService))
    ],
    user_id: Annotated[str, Depends(get_user_id)],
) -> Optional[TransactionRead]:
    await check_ownership(svc=svc, resource_id=transaction_id, user_id=user_id)
    await check_ownership(svc=category_svc, resource_id=category_ids, user_id=user_id)
    return await svc.update_transaction_categories(
        transaction_id=transaction_id, category_ids=category_ids
    )
