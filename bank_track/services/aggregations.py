from datetime import date
from typing import Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bank_track.core.models.sql import (
    ExpenseCategorySQL,
    TransactionSQL,
    transaction_category_link,
)
from bank_track.core.schemas.aggregations import SpendingByCategory


class TransactionAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_speding_by_categories(
        self,
        user_id: str,
        account_id: str | list[str],
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[SpendingByCategory]:
        conditions = [TransactionSQL.user_id == user_id]

        if account_id:
            if isinstance(account_id, str):
                conditions.append(TransactionSQL.account_id == account_id)
            elif isinstance(account_id, list):
                conditions.append(TransactionSQL.account_id.in_(account_id))
        if date_from:
            conditions.append(TransactionSQL.booking_date >= date_from)
        if date_to:
            conditions.append(TransactionSQL.booking_date <= date_to)

        group = case(
            (
                ExpenseCategorySQL.category_name.is_not(None),
                ExpenseCategorySQL.category_name,
            ),
            else_="Uncategorized",
        )
        aggregator = func.sum(TransactionSQL.amount)

        stmt = (
            select(
                group.label("category_name"),
                aggregator.label("amount"),
            )
            .join(
                transaction_category_link,
                ExpenseCategorySQL.category_id
                == transaction_category_link.c.category_id,
                isouter=True,
                full=True,
            )
            .join(
                TransactionSQL,
                TransactionSQL.transaction_id
                == transaction_category_link.c.transaction_id,
                isouter=True,
                full=True,
            )
            .where(*conditions)
            .group_by(ExpenseCategorySQL.category_id, ExpenseCategorySQL.category_name)
            .order_by(aggregator.desc())
        )

        result = (await self.session.execute(stmt)).all()

        return [SpendingByCategory(**row._asdict()) for row in result]

    async def get_spending_by_categories_time_grouped(
        self,
        user_id: str,
        account_id: str | list[str],
        date_group: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[SpendingByCategory]:
        conditions = [TransactionSQL.user_id == user_id]

        if account_id:
            if isinstance(account_id, str):
                conditions.append(TransactionSQL.account_id == account_id)
            elif isinstance(account_id, list):
                conditions.append(TransactionSQL.account_id.in_(account_id))
        if date_from:
            conditions.append(TransactionSQL.booking_date >= date_from)
        if date_to:
            conditions.append(TransactionSQL.booking_date <= date_to)

        group = case(
            (
                ExpenseCategorySQL.category_name.is_not(None),
                ExpenseCategorySQL.category_name,
            ),
            else_="Uncategorized",
        )
        aggregator = func.sum(TransactionSQL.amount)

        stmt = (
            select(
                func.extract(date_group, TransactionSQL.value_date).label("date_group"),
                group.label("category_name"),
                aggregator.label("amount"),
            )
            .join(
                transaction_category_link,
                ExpenseCategorySQL.category_id
                == transaction_category_link.c.category_id,
                isouter=True,
                full=True,
            )
            .join(
                TransactionSQL,
                TransactionSQL.transaction_id
                == transaction_category_link.c.transaction_id,
                isouter=True,
                full=True,
            )
            .where(*conditions)
            .group_by(
                func.extract(date_group, TransactionSQL.value_date),
                ExpenseCategorySQL.category_id,
                ExpenseCategorySQL.category_name,
            )
            .order_by("date_group")
        )

        result = (await self.session.execute(stmt)).all()

        return [SpendingByCategory(**row._asdict()) for row in result]
