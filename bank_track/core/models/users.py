from uuid import UUID

from pydantic import Field

from bank_track.core.models.accounts import Account
from bank_track.core.models.base import BaseDomainModel


class ClerkBaseUser(BaseDomainModel):
    id: str = Field(alias="user_id", pattern=r"^user_[a-zA-Z0-9]{27}$")


class ClerkUserCreate(ClerkBaseUser):
    pass


class ClerkUserRead(ClerkBaseUser):
    accounts: list["Account"] = []


class AccountsRequisition(BaseDomainModel):
    user_id: str = Field(pattern=r"^user_[a-zA-Z0-9]{27}$")
    id: UUID = Field(alias="requisition_id")
    institution_id: str
    agreement_id: UUID
    accepted: bool = False
