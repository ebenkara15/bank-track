from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from bank_track.api.database import get_service
from bank_track.api.query import DateGroup, DateRangeDep
from bank_track.api.security import get_user_id
from bank_track.core.schemas.aggregations import SpendingByCategory
from bank_track.services.aggregations import TransactionAnalyticsService

router = APIRouter(prefix="/aggregations", tags=["aggregations"])


@router.get(
    "/spending_category", description="Get the amount of money spent by category."
)
async def spending_by_category(
    account_id: Annotated[
        str | list[str],
        Query(
            description="The ID of the account. Can be either a single account ID or a list of account IDs."
        ),
    ],
    date_range: DateRangeDep,
    # date_range: Annotated[
    #     DateRangeFilter, Query(description="The date range to be used for filtering.")
    # ],
    svc: Annotated[
        TransactionAnalyticsService, Depends(get_service(TransactionAnalyticsService))
    ],
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[SpendingByCategory] | None:
    if user_id:
        return await svc.get_speding_by_categories(
            user_id=user_id,
            account_id=account_id,
            date_from=date_range.date_from,
            date_to=date_range.date_to,
        )

    raise HTTPException(status_code=404, detail="User not found.")


@router.get(
    "/spending_category_time_group",
    description="Get the amount of money spent by category, grouped by the given `date_group`.",
)
async def spending_by_category_and_time_group(
    account_id: Annotated[
        str | list[str],
        Query(
            description="The ID of the account. Can be either a single account ID or a list of account IDs."
        ),
    ],
    date_range: DateRangeDep,
    # date_range: Annotated[
    #     DateRangeFilter, Query(description="The date range to be used for filtering.")
    # ],
    date_group: Annotated[
        DateGroup,
        Query(
            description="The time part to be used for the aggregation. Defaults to day"
        ),
    ],
    svc: Annotated[
        TransactionAnalyticsService, Depends(get_service(TransactionAnalyticsService))
    ],
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[SpendingByCategory] | None:
    if user_id:
        return await svc.get_spending_by_categories_time_grouped(
            user_id=user_id,
            account_id=account_id,
            date_group=date_group.value,
            date_from=date_range.date_from,
            date_to=date_range.date_to,
        )

    raise HTTPException(status_code=404, detail="User not found.")
