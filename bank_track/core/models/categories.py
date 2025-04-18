from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import Field

from bank_track.core.models.base import BaseDomainModel

if TYPE_CHECKING:
    from bank_track.core.models.transactions import Transaction


class ExpenseCategory(BaseDomainModel, use_enum_values=True):
    """The minimal representation of an Expense Category."""

    id: UUID = Field(alias="category_id", default_factory=uuid4)
    category_name: str
    category_description: str


class ExpenseCategoryCreate(ExpenseCategory):
    user_id: Optional[str] = Field(pattern=r"user_[a-zA-Z0-9]{27}$", default=None)


class ExpenseCategoryUpdate(ExpenseCategory):
    user_id: Optional[str] = Field(pattern=r"user_[a-zA-Z0-9]{27}$", default=None)


class ExpenseCategoryRead(ExpenseCategory):
    user_id: Optional[str] = Field(pattern=r"user_[a-zA-Z0-9]{27}$", default=None)
    # transactions: Optional[list[Transaction]] = None
