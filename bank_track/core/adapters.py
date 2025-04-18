from abc import ABC, abstractmethod
from typing import Generic, List, Literal, Optional, Self, Type, TypeVar
from uuid import UUID

import sqlalchemy
from sqlalchemy import Column, func, select
from sqlalchemy.orm import Mapped, Session

from bank_track.core.models.accounts import AccountRead
from bank_track.core.models.balances import BalanceRead
from bank_track.core.models.base import BaseDomainModel
from bank_track.core.models.categories import ExpenseCategoryRead
from bank_track.core.models.sql import (
    AccountSQL,
    BalanceSQL,
    BaseSQLModel,
    ExpenseCategorySQL,
    RequisitionSQL,
    TransactionSQL,
    UserSQL,
)
from bank_track.core.models.transactions import TransactionRead
from bank_track.core.models.types import BalanceType
from bank_track.core.models.users import AccountsRequisition
from bank_track.core.models.users import ClerkUserRead as User

ModelReadType = TypeVar("ModelReadType", bound=BaseDomainModel)
ModelUpdateType = TypeVar("ModelUpdateType", bound=BaseDomainModel)
ModelCreateType = TypeVar("ModelCreateType", bound=BaseDomainModel)
S = TypeVar("S", bound=BaseSQLModel)


class BaseSQLService(ABC, Generic[ModelReadType, S]):
    """Base class for SQL services.
    It provides the basic CRUD operations for the SQL models.

    Attributes:
        db_model (BaseSQLModel): The SQLAlchemy model.
        domain_model (BaseModel): The Pydantic model.
    """

    db_model: Type[S]
    domain_model: Type[ModelReadType]

    def __init__(self, sql_session: Session) -> None:
        """Initializes the SQL service.

        Args:
            sql_session (Session): The SQLAlchemy session.
        """
        self.sql_session = sql_session

    def __call__(self) -> Self:
        """Returns the instance of the service."""
        return self

    def _to_model(self, obj: S) -> ModelReadType:
        """Converts a SQLAlchemy model to a Pydantic model.

        Args:
            obj (BaseSQLModel): The SQLAlchemy model.
        """
        return self.domain_model.model_validate(obj, from_attributes=True)

    def statement_builder(
        self,
        statement: sqlalchemy.Select,
        limit: Optional[int],
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
    ) -> sqlalchemy.Select:
        """Builds the SQL statement. It adds the limit, order by and sort type to the statement.

        Args:
            statement (sqlalchemy.Select): The SQL statement.
            limit (int): The limit of the statement.
            order_by (sqlalchemy.Column or sqlalchemy.orm.Mapped): The column to order by.
            sort_type (str): The sort type.
        """
        if limit:
            statement = statement.limit(limit)

        if order_by:
            if sort_type == "asc":
                statement = statement.order_by(order_by.asc())
            elif sort_type == "desc":
                statement = statement.order_by(order_by.desc())

        return statement

    def parse_conditions_args(self, **kwargs: Column | Mapped) -> list:
        """Parses the conditions arguments.

        Args:
            **kwargs (Column or Mapped): The conditions arguments.

        Example:
            parse_conditions_args(column1=value1, column2=value2)
        """
        conditions = []
        for column, value in kwargs.items():
            if isinstance(value, list):
                conditions.append((getattr(self.db_model, column)).in_(value))
            else:
                conditions.append(getattr(self.db_model, column) == value)

        return conditions

    def get(self, id: str | UUID) -> Optional[ModelReadType]:
        """Gets an object by its ID.

        Args:
            id (str or UUID): The object ID.
        """
        db_obj = self.sql_session.get(entity=self.db_model, ident=id)
        return self._to_model(db_obj) if db_obj else None

    def get_by(self, **kwargs) -> Optional[ModelReadType]:
        """Gets an object by its attributes.

        Args:
            **kwargs: The attributes.

        Example:
            ```
            get_by(column1=value1, column2=value2)
            ```
        """
        conditions = self.parse_conditions_args(**kwargs)

        db_obj = self.sql_session.scalars(
            select(self.db_model).where(*conditions)
        ).first()
        return self._to_model(db_obj) if db_obj else None

    @abstractmethod
    def list(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
    ) -> List[ModelReadType]:
        """Lists the objects.

        Args:
            limit (int): The limit length of the list. Default to `100`.
            order_by (Column or Mapped, optional): The column to order by.
            sort_type ("asc" or "desc", optional): The sort type to apply.
        """
        raise NotImplementedError

    @abstractmethod
    def list_by(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
        **kwargs,
    ) -> List[ModelReadType]:
        """Lists the objects filter by the attributes.

        Args:
            limit (int): The limit length of the list. Defaults to `100`.
            order_by (Column or Mapped, optional): The column to order by.
            sort_type (str): The sort type to apply. Defaults to "asc".
            **kwargs (Column or Mapped): The attributes.

        Example:
            ```
            list_by(limit=10, order_by=model.Column1, column1=value1, column2=value2, column3=value3)
            ```
        """
        raise NotImplementedError

    def create(self, obj: ModelCreateType) -> ModelReadType:
        """Creates an object.

        Args:
            obj (BaseModel): The object to create.
        """
        db_obj = self.db_model(**obj.model_dump(by_alias=True))
        self.sql_session.add(db_obj)
        self.sql_session.commit()
        self.sql_session.refresh(db_obj)
        return self._to_model(db_obj)

    def update(self, obj: ModelUpdateType) -> ModelReadType | None:
        """Updates an object.

        Args:
            obj (BaseModel): The object to update.
        """
        db_obj = self.sql_session.get(self.db_model, obj.id)

        if db_obj:
            db_obj.update_from_dict(**obj.model_dump(by_alias=True))
            self.sql_session.add(db_obj)
            self.sql_session.commit()
            self.sql_session.refresh(db_obj)
            return self._to_model(db_obj)
        else:
            return None

    def delete(self, id: str | UUID) -> ModelReadType | None:
        """Deletes an object by its ID.

        Args:
            id (str or UUID): The object ID.
        """
        db_obj = self.sql_session.get(self.db_model, id)
        self.sql_session.delete(db_obj)
        self.sql_session.commit()
        return self._to_model(db_obj) if db_obj else None

    def upsert(self, obj: ModelUpdateType | ModelCreateType) -> ModelReadType | None:
        """Updates or creates an object.

        Args:
            obj (BaseModel): The object to update or create.
        """
        db_obj = self.sql_session.get(self.db_model, obj.id)

        if db_obj:
            db_obj.update_from_dict(**obj.model_dump(by_alias=True))
            self.sql_session.add(db_obj)
            self.sql_session.commit()
            self.sql_session.refresh(db_obj)
            return self._to_model(db_obj)
        else:
            db_obj = self.db_model(**obj.model_dump(by_alias=True))
            self.sql_session.add(db_obj)
            self.sql_session.commit()
            self.sql_session.refresh(db_obj)
            return self._to_model(db_obj)


class TransactionSQLService(BaseSQLService[TransactionRead, TransactionSQL]):
    db_model = TransactionSQL
    domain_model = TransactionRead

    def list(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
    ) -> list[TransactionRead]:
        statement = select(self.db_model)
        statement = self.statement_builder(
            statement, limit=limit, order_by=order_by, sort_type=sort_type
        )
        db_objs = self.sql_session.scalars(
            select(self.db_model).limit(limit).order_by(self.db_model.value_date.desc())
        ).all()
        return [self._to_model(db_obj) for db_obj in db_objs]

    def list_by(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc", "desc"] | None = "asc",
        **kwargs,
    ) -> List[TransactionRead]:
        conditions = self.parse_conditions_args(**kwargs)

        statement = select(self.db_model).where(*conditions)
        statement = self.statement_builder(
            statement, limit=limit, order_by=order_by, sort_type=sort_type
        )

        db_objs = self.sql_session.scalars(statement).all()
        return [self._to_model(db_obj) for db_obj in db_objs]

    # TODO: move to category adapter
    def update_transaction_categories(
        self, transaction_id: UUID, category_ids: List[UUID]
    ) -> TransactionRead | None:
        categories_statement = select(ExpenseCategorySQL).where(
            ExpenseCategorySQL.category_id.in_(category_ids)
        )
        categories = list(self.sql_session.scalars(categories_statement).all())

        db_obj = self.sql_session.get(TransactionSQL, transaction_id)
        if db_obj:
            db_obj.categories = categories
            self.sql_session.add(db_obj)
            self.sql_session.commit()
            self.sql_session.refresh(db_obj)
            return self._to_model(db_obj)
        else:
            return None


class BalanceSQLService(BaseSQLService[BalanceRead, BalanceSQL]):
    db_model = BalanceSQL
    domain_model = BalanceRead

    def get_latest_by_account_id(self, account_id: str) -> list[BalanceRead]:
        latest_balances_by_group = (
            select(
                BalanceSQL.balance_type,
                func.max(BalanceSQL.reference_date).label("max_reference_date"),
            )
            .where(BalanceSQL.account_id == account_id)
            .group_by(BalanceSQL.balance_type)
        ).alias("latest_balances")

        db_objs = self.sql_session.scalars(
            select(BalanceSQL)
            .join(
                latest_balances_by_group,
                (BalanceSQL.balance_type == latest_balances_by_group.c.balance_type)
                & (
                    BalanceSQL.reference_date
                    == latest_balances_by_group.c.max_reference_date
                ),
            )
            .where(BalanceSQL.account_id == account_id)
        ).all()

        return [self._to_model(db_obj) for db_obj in db_objs]

    def get_latest_by_account_id_and_type(
        self, account_id: str, balance_type: BalanceType
    ) -> Optional[BalanceRead]:
        db_obj = self.sql_session.scalars(
            select(BalanceSQL)
            .where(BalanceSQL.account_id == account_id)
            .where(BalanceSQL.balance_type == balance_type)
            .order_by(BalanceSQL.reference_date.desc())
            .limit(1)
        ).one_or_none()

        return self._to_model(db_obj) if db_obj else None

    def list(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
    ) -> List[BalanceRead]:
        db_objs = self.sql_session.scalars(
            select(BalanceSQL).order_by(BalanceSQL.reference_date.desc())
        ).all()

        return [self._to_model(db_obj) for db_obj in db_objs]

    def list_by(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
        **kwargs,
    ) -> List[BalanceRead]:
        conditions = self.parse_conditions_args(**kwargs)
        for column, value in kwargs.items():
            if isinstance(value, list):
                conditions.append((getattr(BalanceSQL, column)).in_(value))
            else:
                conditions.append(getattr(BalanceSQL, column) == value)

        db_objs = self.sql_session.scalars(
            select(BalanceSQL)
            .where(*conditions)
            .order_by(BalanceSQL.reference_date.desc())
        ).all()

        return [self._to_model(db_obj) for db_obj in db_objs]


class AccountSQLService(BaseSQLService[AccountRead, AccountSQL]):
    db_model = AccountSQL
    domain_model = AccountRead

    def list(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
    ) -> List[AccountRead]:
        db_objs = self.sql_session.scalars(
            select(AccountSQL).order_by(AccountSQL.created_at.desc())
        ).all()

        return [self._to_model(db_obj) for db_obj in db_objs]

    def list_by(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
        **kwargs,
    ) -> List[AccountRead]:
        conditions = [getattr(AccountSQL, key) == value for key, value in kwargs.items()]
        db_objs = self.sql_session.scalars(
            select(AccountSQL).where(*conditions).order_by(AccountSQL.created_at.desc())
        ).all()

        return [self._to_model(db_obj) for db_obj in db_objs]


class UserSQLService(BaseSQLService[User, UserSQL]):
    db_model = UserSQL
    domain_model = User

    # def get_by_email(self, email: str) -> Optional[User]:
    #     db_obj = self.sql_session.scalars(
    #         select(UserSQL).where(func.lower(UserSQL.email) == func.lower(email))
    #     ).first()
    #     return self._to_model(db_obj) if db_obj else None

    # def list_accounts(self, user_id: str) -> List[AccountRead]:
    #     accounts = self.sql_session.scalars(
    #         select(AccountSQL.account_id).where(AccountSQL.user_id == user_id)
    #     ).all()

    #     return [self._to_model(account) for account in accounts]

    # def list_balances(self, user_id: str) -> List[BalanceRead]:
    #     return self.sql_session.scalars(
    #         select(BalanceSQL.balance_id).where(BalanceSQL.user_id == user_id)
    #     ).all()

    # def list_transactions(self, user_id: str) -> List[TransactionRead]:
    #     return self.sql_session.scalars(
    #         select(TransactionSQL.transaction_id).where(
    #             TransactionSQL.user_id == user_id
    #         )
    #     ).all()

    def list(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
    ) -> list[User]:
        db_objs = self.sql_session.scalars(select(UserSQL)).all()

        return [self._to_model(db_obj) for db_obj in db_objs]

    def list_by(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
        **kwargs,
    ) -> List[User]:
        conditions = [getattr(UserSQL, key) == value for key, value in kwargs.items()]
        db_objs = self.sql_session.scalars(select(UserSQL).where(*conditions)).all()

        return [self._to_model(db_obj) for db_obj in db_objs]


class ExpenseCategorySQLService(BaseSQLService[ExpenseCategoryRead, ExpenseCategorySQL]):
    db_model = ExpenseCategorySQL
    domain_model = ExpenseCategoryRead

    def list(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
    ) -> List[ExpenseCategoryRead]:
        db_objs = self.sql_session.scalars(select(ExpenseCategorySQL)).all()
        return [self._to_model(db_obj) for db_obj in db_objs]

    def list_by(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
        **kwargs,
    ) -> List[ExpenseCategoryRead]:
        conditions = [
            getattr(ExpenseCategorySQL, key) == value for key, value in kwargs.items()
        ]
        db_objs = self.sql_session.scalars(
            select(ExpenseCategorySQL).where(*conditions)
        ).all()
        return [self._to_model(db_obj) for db_obj in db_objs]


class RequisitionSQLService(BaseSQLService[AccountsRequisition, RequisitionSQL]):
    db_model = RequisitionSQL
    domain_model = AccountsRequisition

    def get(self, id: str | UUID) -> Optional[AccountsRequisition]:
        db_obj = self.sql_session.get(RequisitionSQL, id)
        return self._to_model(db_obj) if db_obj else None

    def list(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
    ) -> List[AccountsRequisition]:
        db_objs = self.sql_session.scalars(select(RequisitionSQL))
        return [self._to_model(db_obj) for db_obj in db_objs]

    def list_by(
        self,
        limit: int = 100,
        order_by: Optional[Column | Mapped] = None,
        sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
        **kwargs,
    ) -> List[AccountsRequisition]:
        conditions = [
            getattr(RequisitionSQL, key) == value for key, value in kwargs.items()
        ]
        db_objs = self.sql_session.scalars(select(RequisitionSQL).where(*conditions))
        return [self._to_model(db_obj) for db_obj in db_objs]
