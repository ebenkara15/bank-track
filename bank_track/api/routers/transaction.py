from typing import Annotated, Literal, Optional
from uuid import UUID

from fastapi import Body, Depends, HTTPException, Path, Query
from fastapi.routing import APIRouter

from bank_track.api.database import get_service
from bank_track.api.exceptions import raise_on_no_return
from bank_track.api.security import get_user_id
from bank_track.core.adapters import TransactionSQLService
from bank_track.core.models.sql import TransactionSQL
from bank_track.core.models.transactions import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.get(
    "/{transaction_id}",
    description="Get a transaction by its ID. The transaction must be belong to the connected user through his JWT.",
)
@raise_on_no_return
def get_transaction(
    transaction_id: Annotated[
        UUID, Path(description="The ID of the transaction. Must be a UUID.")
    ],
    svc: TransactionSQLService = Depends(get_service(TransactionSQLService)),
    user_id: str = Depends(get_user_id),
) -> Optional[TransactionRead]:
    if user_id:
        return svc.get_by(user_id=user_id, transaction_id=transaction_id)
    raise HTTPException(status_code=404, detail="User not found")


@router.get(
    "/",
    description="List all transactions that belong to the connected user through his JWT. Result is sorted by the time of the transactions.",
)
def get_all_transactions(
    svc: TransactionSQLService = Depends(get_service(TransactionSQLService)),
    user_id: str = Depends(get_user_id),
    limit: Annotated[
        int, Query(description="Maximum number of transactions to retrieve.")
    ] = 100,
    # order_by: TransactionSQL = TransactionSQL.value_date,
    sort_type: Annotated[
        Literal["asc", "desc"] | None,
        Query(description="The sort direction. One of `'asc'` or `'desc'`"),
    ] = "desc",
) -> list[TransactionRead]:
    if user_id:
        return svc.list_by(
            user_id=user_id,
            limit=limit,
            order_by=TransactionSQL.value_date,
            sort_type=sort_type,
        )
    raise HTTPException(status_code=404, detail="User not found")


@router.get(
    "/accounts/{account_id}",
    description="List all transactions for the given `account_id` for the connected user through his JWT.",
)
def list_transactions_by_account(
    account_id: Annotated[str, Path(description="The ID of the account.")],
    svc: TransactionSQLService = Depends(get_service(TransactionSQLService)),
    user_id: str = Depends(get_user_id),
) -> list[TransactionRead]:
    if user_id:
        return svc.list_by(account_id=account_id, user_id=user_id)

    raise HTTPException(status_code=404, detail="User not found")


@router.get(
    "/accounts/f/",
    description="List all transactions for the given list of account ID for the connected user through his JWT.",
)
def list_transactions_by_accounts(
    account_ids: Annotated[
        list[str],
        Query(description="The account IDs from which to retrieve the transactions"),
    ],
    svc: TransactionSQLService = Depends(get_service(TransactionSQLService)),
    user_id: str = Depends(get_user_id),
) -> list[TransactionRead]:
    if user_id:
        return svc.list_by(account_id=account_ids, user_id=user_id)

    raise HTTPException(status_code=404, detail="User not found")


@router.post(
    "/", description="Create a transaction for the connected user through his JWT."
)
def create_transaction(
    transaction: Annotated[
        TransactionCreate, Body(description="The transaction to create.")
    ],
    svc: TransactionSQLService = Depends(get_service(TransactionSQLService)),
    user_id: str = Depends(get_user_id),
) -> TransactionRead:
    if user_id:
        transaction.user_id = user_id
        return svc.create(transaction)

    raise HTTPException(status_code=404, detail="User not found")


@router.put(
    "/", description="Update a transaction for the connected user through his JWT."
)
def update_transaction(
    transaction: Annotated[
        TransactionUpdate,
        Body(
            description="The updated transaction. The previous transaction is identified by the `TransactionUpdate.transaction_id` field."
        ),
    ],
    svc: TransactionSQLService = Depends(get_service(TransactionSQLService)),
    user_id: str = Depends(get_user_id),
) -> Optional[TransactionRead]:
    if user_id:
        transaction.user_id = user_id
        return svc.update(transaction)

    raise HTTPException(status_code=404, detail="User not found")


@router.put(
    "/{transaction_id}/classify",
    description="Classify the transaction identified by its `transaction_id` with the given categories identified by the `category_ids` list.",
)
def update_transaction_categories(
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
    svc: TransactionSQLService = Depends(get_service(TransactionSQLService)),
    user_id: str = Depends(get_user_id),
) -> Optional[TransactionRead]:
    if user_id:
        return svc.update_transaction_categories(
            transaction_id=transaction_id, category_ids=category_ids
        )

    raise HTTPException(status_code=404, detail="User not found")
