from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from bank_track.core.models.types import BalanceType, CashAccountType, CurrencyType


class BaseSQLModel(DeclarativeBase):
    def update_from_dict(self, **kwargs: dict):
        for key, value in kwargs.items():
            if hasattr(self, key) and value:
                setattr(self, key, value)


class UserSQL(BaseSQLModel):
    __tablename__ = "users"

    user_id = Column(Text, primary_key=True, index=True)
    accounts = relationship("AccountSQL", back_populates="user", lazy="selectin")


class UserScopeMixin:
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"), index=True, nullable=False
    )


class AccountSQL(BaseSQLModel, UserScopeMixin):
    __tablename__ = "accounts"

    account_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    provider_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), default=uuid4)
    iban: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    name: Mapped[str] = mapped_column(String, index=True)
    currency: Mapped[CurrencyType] = mapped_column(Enum(CurrencyType))
    product: Mapped[str] = mapped_column(String)
    account_type: Mapped[CashAccountType] = mapped_column(Enum(CashAccountType))
    linked_account: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    usage: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_modified: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    access: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["UserSQL"] = relationship(back_populates="accounts")
    balances: Mapped[list["BalanceSQL"]] = relationship(back_populates="account")
    transactions: Mapped[list["TransactionSQL"]] = relationship(
        back_populates="account"
    )


class BalanceSQL(BaseSQLModel, UserScopeMixin):
    __tablename__ = "balances"

    balance_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[CurrencyType] = mapped_column(Enum(CurrencyType))
    reference_date: Mapped[date] = mapped_column(Date, index=True)
    balance_type: Mapped[Optional[BalanceType]] = mapped_column(
        Enum(BalanceType), default=None
    )

    # Only `created_at` is needed since the balance is immutable
    # and is a snapshot of the account balance at a given date
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    account_id: Mapped[str] = mapped_column(
        String, ForeignKey("accounts.account_id"), index=True
    )
    account: Mapped["AccountSQL"] = relationship(back_populates="balances")


transaction_category_link = Table(
    "transaction_category_link",
    BaseSQLModel.metadata,
    Column(
        "transaction_id",
        Uuid,
        ForeignKey("transactions.transaction_id"),
        primary_key=True,
    ),
    Column(
        "category_id",
        Uuid,
        ForeignKey("expense_categories.category_id"),
        primary_key=True,
    ),
)


class ExpenseCategorySQL(BaseSQLModel, UserScopeMixin):
    __tablename__ = "expense_categories"

    category_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    category_name: Mapped[str] = mapped_column(String, index=True)
    category_description: Mapped[Optional[str]] = mapped_column(String, default=None)

    transactions: Mapped[list["TransactionSQL"]] = relationship(
        "TransactionSQL",
        back_populates="categories",
        secondary=transaction_category_link,
    )

    __table_args__ = (
        UniqueConstraint(
            "category_name",
            "user_id",
            name="unique_category_name_per_user",
        ),
    )


class TransactionSQL(BaseSQLModel, UserScopeMixin):
    __tablename__ = "transactions"

    transaction_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[CurrencyType] = mapped_column(Enum(CurrencyType))
    booking_date: Mapped[date] = mapped_column(Date, index=True)
    value_date: Mapped[date] = mapped_column(Date, index=True)
    transaction_type: Mapped[Optional[str]] = mapped_column(String, default=None)

    categories: Mapped[list["ExpenseCategorySQL"]] = relationship(
        "ExpenseCategorySQL",
        back_populates="transactions",
        secondary=transaction_category_link,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_modified: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    account_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("accounts.account_id"), index=True
    )
    account: Mapped["AccountSQL"] = relationship(
        "AccountSQL", back_populates="transactions"
    )


class RequisitionSQL(BaseSQLModel, UserScopeMixin):
    __tablename__ = "requisitions"

    requisition_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    agreement_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    institution_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_modified: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )


if __name__ == "__main__":
    engine = create_engine("postgresql://postgres:password@localhost/postgres")

    BaseSQLModel.metadata.drop_all(engine)
    BaseSQLModel.metadata.create_all(engine)
