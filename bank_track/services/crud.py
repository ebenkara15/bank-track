from abc import ABC
from typing import Generic, List, Optional, Self, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from bank_track.api.page import PaginatedResponse, PaginationMetadata
from bank_track.api.query import OrderingFilter
from bank_track.core.models.sql import (
    AccountSQL,
    BalanceSQL,
    BaseSQLModel,
    ExpenseCategorySQL,
    RequisitionSQL,
    TransactionSQL,
    UserSQL,
)
from bank_track.core.schemas.accounts import AccountRead
from bank_track.core.schemas.balances import BalanceRead
from bank_track.core.schemas.base import BaseDomainModel
from bank_track.core.schemas.categories import ExpenseCategoryRead
from bank_track.core.schemas.transactions import TransactionRead
from bank_track.core.schemas.types import BalanceType
from bank_track.core.schemas.users import AccountsRequisition
from bank_track.core.schemas.users import ClerkUserRead as User
from bank_track.services.filtering import QueryFilter

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
        selectinoad_cols (Sequece): A sequence of relationships to eager load.
    """

    db_model: Type[S]
    domain_model: Type[ModelReadType]
    selectinload_cols: Sequence[InstrumentedAttribute] | None

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the SQL service.

        Args:
            session (Session): The SQLAlchemy session.
        """
        self.session = session
        self.selectinload_opts = (
            [selectinload(col) for col in self.selectinload_cols]  # type: ignore
            if self.selectinload_cols
            else []
        )
        self.selectinload_attributes: list[str] | None = (
            [col.property.key for col in self.selectinload_cols]
            if self.selectinload_cols
            else None
        )

    def __call__(self) -> Self:
        """Returns the instance of the service."""
        return self

    def _to_model(self, obj: S) -> ModelReadType:
        """Converts a SQLAlchemy model to a Pydantic model.

        Args:
            obj (BaseSQLModel): The SQLAlchemy model.
        """
        return self.domain_model.model_validate(obj, from_attributes=True)

    async def _get_pagination_metadata(
        self, statement: Select, result_count: int
    ) -> PaginationMetadata:
        """Returns the pagination metadata like total number of rows found, limit and offset.

        Args:
            statement (sqlalchemy.Select): The select statement to be paginated.
            result_count (int): The number of results retrieved with the `statement`.
        """

        limit, offset = statement._limit or 0, statement._offset or 0

        total_statement = (
            select(func.count())
            .select_from(self.db_model)
            .where(*statement._where_criteria)
        )

        total = (await self.session.execute(total_statement)).scalar_one()

        return PaginationMetadata(
            limit=limit, offset=offset, count=result_count, total=total
        )

    async def get(self, id: str | UUID) -> Optional[ModelReadType]:
        """Gets an object by its ID.

        Args:
            id (str or UUID): The object ID.
        """
        db_obj = await self.session.get(
            entity=self.db_model, ident=id, options=self.selectinload_opts
        )
        return self._to_model(db_obj) if db_obj else None

    async def get_by(self, **kwargs) -> Optional[ModelReadType]:
        """Gets an object by its attributes.

        Args:
            **kwargs: The attributes.

        Example:
            ```
            >>> get_by(column1=value1, column2=value2)
            ```
        """
        conditions = QueryFilter.parse_filters(**kwargs)

        result = await self.session.execute(
            select(self.db_model).where(*conditions).options(*self.selectinload_opts)
        )
        db_obj = result.scalars().first()
        return self._to_model(db_obj) if db_obj else None

    async def list(
        self, ordering: OrderingFilter = OrderingFilter(), paginate: bool = False
    ) -> List[ModelReadType] | PaginatedResponse[ModelReadType]:
        """Lists the objects.

        Args:
            ordering (OrderingFilter): The OrderingFilter object to be used for filter results like limit, offset and sorting.
        """
        statement = select(self.db_model).options(*self.selectinload_opts)
        statement = QueryFilter.parse_ordering(
            db_model=self.db_model, statement=statement, ordering=ordering
        )

        result = await self.session.execute(statement)
        db_objs = [self._to_model(db_obj) for db_obj in result.scalars().all()]

        if paginate:
            pagination_metadata = await self._get_pagination_metadata(
                statement, len(db_objs)
            )
            return PaginatedResponse(data=db_objs, pagination=pagination_metadata)

        return db_objs

    async def list_by(
        self,
        ordering: OrderingFilter = OrderingFilter(),
        paginate: bool = False,
        **kwargs,
    ) -> List[ModelReadType] | PaginatedResponse[ModelReadType]:
        """Lists the objects filtered by the attributes.

        Args:
            ordering (OrderingFilter): The OrderingFilter object to be used for filter results like limit, offset and sorting.
            paginate (bool): Indicates whether the results should be paginated or not. Default to `False`
            **kwargs (Column or Mapped): The attributes for filtering.

        Example:
            ```
            >>> ordering = OrderingFilter(limit=10, order_by=model.Column1)
            >>> list_by(ordering=ordering, column2__gte=value2, column3__lt=value3)
            ```
        """
        conditions = QueryFilter.parse_filters(self.db_model, **kwargs)

        statement = (
            select(self.db_model).where(*conditions).options(*self.selectinload_opts)
        )
        statement = QueryFilter.parse_ordering(
            db_model=self.db_model, statement=statement, ordering=ordering
        )

        result = await self.session.execute(statement)
        db_objs = [self._to_model(db_obj) for db_obj in result.scalars().all()]

        if paginate:
            pagination_metadata = await self._get_pagination_metadata(
                statement, len(db_objs)
            )
            return PaginatedResponse(data=db_objs, pagination=pagination_metadata)

        return db_objs

    async def create(self, obj: ModelCreateType) -> ModelReadType:
        """Creates an object.

        Args:
            obj (BaseModel): The object to create.
        """
        db_obj = self.db_model(**obj.model_dump(by_alias=True))
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj, attribute_names=self.selectinload_attributes)
        return self._to_model(db_obj)

    async def update(self, obj: ModelUpdateType) -> ModelReadType | None:
        """Updates an object.

        Args:
            obj (BaseModel): The object to update.
        """
        db_obj = await self.session.get(
            self.db_model, obj.id, options=self.selectinload_opts
        )

        if db_obj:
            db_obj.update_from_dict(**obj.model_dump(by_alias=True))
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(
                db_obj, attribute_names=self.selectinload_attributes
            )
            return self._to_model(db_obj)
        else:
            return None

    async def delete(self, id: str | UUID) -> ModelReadType | None:
        """Deletes an object by its ID.

        Args:
            id (str or UUID): The object ID.
        """
        db_obj = await self.session.get(
            self.db_model, id, options=self.selectinload_opts
        )
        await self.session.delete(db_obj)
        await self.session.commit()
        return self._to_model(db_obj) if db_obj else None

    async def upsert(
        self, obj: ModelUpdateType | ModelCreateType
    ) -> ModelReadType | None:
        """Updates or creates an object.

        Args:
            obj (BaseModel): The object to update or create.
        """
        db_obj = await self.session.get(
            self.db_model, obj.id, options=self.selectinload_opts
        )

        if db_obj:
            db_obj.update_from_dict(**obj.model_dump(by_alias=True))
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(
                db_obj, attribute_names=self.selectinload_attributes
            )
            return self._to_model(db_obj)
        else:
            db_obj = self.db_model(**obj.model_dump(by_alias=True))
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(
                db_obj, attribute_names=self.selectinload_attributes
            )
            return self._to_model(db_obj)


class TransactionSQLService(BaseSQLService[TransactionRead, TransactionSQL]):
    db_model = TransactionSQL
    domain_model = TransactionRead
    selectinload_cols = [TransactionSQL.account, TransactionSQL.categories]

    # TODO: move to category adapter
    async def update_transaction_categories(
        self, transaction_id: UUID, category_ids: List[UUID]
    ) -> TransactionRead | None:
        categories_statement = select(ExpenseCategorySQL).where(
            ExpenseCategorySQL.category_id.in_(category_ids)
        )
        result = await self.session.execute(categories_statement)
        categories = list(result.scalars().all())

        db_obj = await self.session.get(
            TransactionSQL, transaction_id, options=self.selectinload_opts
        )
        if db_obj:
            db_obj.categories = categories
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(
                db_obj, attribute_names=self.selectinload_attributes
            )
            return self._to_model(db_obj)
        else:
            return None


class BalanceSQLService(BaseSQLService[BalanceRead, BalanceSQL]):
    db_model = BalanceSQL
    domain_model = BalanceRead
    selectinload_cols = [BalanceSQL.account]

    async def get_latest_by_account_id(self, account_id: str) -> list[BalanceRead]:
        latest_balances_by_group = (
            select(
                BalanceSQL.balance_type,
                func.max(BalanceSQL.reference_date).label("max_reference_date"),
            )
            .where(BalanceSQL.account_id == account_id)
            .group_by(BalanceSQL.balance_type)
        ).alias("latest_balances")

        result = await self.session.execute(
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
            .options(*self.selectinload_opts)
        )

        db_objs = result.scalars().all()

        return [self._to_model(db_obj) for db_obj in db_objs]

    async def get_latest_by_account_id_and_type(
        self, account_id: str, balance_type: BalanceType
    ) -> Optional[BalanceRead]:
        result = await self.session.execute(
            select(BalanceSQL)
            .where(BalanceSQL.account_id == account_id)
            .where(BalanceSQL.balance_type == balance_type)
            .order_by(BalanceSQL.reference_date.desc())
            .limit(1)
            .options(*self.selectinload_opts)
        )
        db_obj = result.scalars().one_or_none()

        return self._to_model(db_obj) if db_obj else None


class AccountSQLService(BaseSQLService[AccountRead, AccountSQL]):
    db_model = AccountSQL
    domain_model = AccountRead
    selectinload_cols = [AccountSQL.balances]


class UserSQLService(BaseSQLService[User, UserSQL]):
    db_model = UserSQL
    domain_model = User
    selectinload_cols = [UserSQL.accounts]

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


class ExpenseCategorySQLService(BaseSQLService[ExpenseCategoryRead, ExpenseCategorySQL]):
    db_model = ExpenseCategorySQL
    domain_model = ExpenseCategoryRead
    selectinload_cols = []


class RequisitionSQLService(BaseSQLService[AccountsRequisition, RequisitionSQL]):
    db_model = RequisitionSQL
    domain_model = AccountsRequisition
    selectinload_cols = []
