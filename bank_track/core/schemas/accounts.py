from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import Field

from bank_track.core.schemas.base import BaseDomainModel
from bank_track.core.schemas.types import CashAccountType, CurrencyType

if TYPE_CHECKING:
    from bank_track.core.schemas.balances import Balance
    from bank_track.core.schemas.transactions import Transaction
    from bank_track.core.schemas.users import ClerkBaseUser


class Account(BaseDomainModel, use_enum_values=True):
    """The Account model defining data provided by GoCardless API."""

    id: str = Field(alias="account_id")
    provider_id: UUID
    iban: Optional[str] = None
    name: str
    currency: CurrencyType
    product: str
    account_type: CashAccountType
    linked_account: Optional[str] = None
    usage: str


class AccountCreate(Account):
    access: bool
    user_id: str = Field(pattern=r"^user_[a-zA-Z0-9]{27}$")


class AccountUpdate(Account):
    access: bool
    user_id: str = Field(pattern=r"^user_[a-zA-Z0-9]{27}$")
    last_modified: datetime = Field(default_factory=datetime.now)


class AccountRead(Account):
    access: bool
    user_id: str = Field(pattern=r"^user_[a-zA-Z0-9]{27}$")
    created_at: datetime
    last_modified: Optional[datetime]
    balances: Optional[list["Balance"]] = None


class AccountFull(Account):
    access: bool
    user_id: str = Field(pattern=r"^user_[a-zA-Z0-9]{27}$")
    created_at: datetime
    last_modified: Optional[datetime] = None
    balances: list["Balance"] = []
    transactions: list["Transaction"] = []
    user: "ClerkBaseUser"
