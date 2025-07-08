from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Literal, Optional
from uuid import UUID

from pydantic import Field

from bank_track.core.schemas.base import BaseDomainModel
from bank_track.core.schemas.categories import ExpenseCategory
from bank_track.core.schemas.types import CurrencyType

if TYPE_CHECKING:
    from bank_track.core.schemas.accounts import Account


class Transaction(BaseDomainModel, use_enum_values=True):
    """The Transaction model defining data provided by GoCardless API."""

    id: UUID = Field(alias="transaction_id")
    amount: Decimal = Field(decimal_places=2)
    currency: CurrencyType
    booking_date: Optional[date] = None
    value_date: Optional[date] = None
    transaction_type: Literal["booked", "pending"]


class TransactionCreate(Transaction):
    """The Transaction model used to create object in DB.

    This model is passed to the corresponding `TransactionSQL`.
    """

    account_id: str
    user_id: str = Field(pattern=r"^user_[a-zA-Z0-9]{27}$")


class TransactionUpdate(Transaction):
    account_id: str
    user_id: str = Field(pattern=r"^user_[a-zA-Z0-9]{27}$")
    categories: list[ExpenseCategory]


class TransactionRead(Transaction):
    """The Transaction read from the DB.

    This model is directly derived from the corresponding `TransactionSQL` model.
    """

    account_id: str
    user_id: str = Field(pattern=r"^user_[a-zA-Z0-9]{27}$")
    created_at: datetime
    last_modified: Optional[datetime] = None
    categories: list[ExpenseCategory]
    account: "Account"
