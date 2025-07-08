from datetime import date
from enum import StrEnum
from typing import Annotated, Literal, Optional, Self

from fastapi import Depends
from pydantic import BaseModel, Field, model_validator


class DateRangeFilter(BaseModel):
    date_from: Optional[date] = Field(description="Start date for filter.", default=None)
    date_to: Optional[date] = Field(description="End date for filter.", default=None)

    @model_validator(mode="after")
    def date_to_is_after_date_from(self) -> Self:
        if (self.date_from and self.date_to) and (self.date_from >= self.date_to):
            raise ValueError("`date_from` must be strictly earlier than `date_to`.")
        return self


class DateGroup(StrEnum):
    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "mounth"
    WEEK = "week"
    DAY = "day"


class OrderingFilter(BaseModel):
    order_by: Optional[str] = Field(
        description="The column to use to order results.", default=None
    )
    sort_type: Optional[Literal["asc", "desc"]] = Field(
        description="The type of sort. Can be wheter `asc` or `desc`", default="desc"
    )
    limit: Optional[int] = Field(
        description="The maximum number of results.", default=None
    )
    offset: Optional[int] = Field(
        description="The offset to apply. To be used with `limit`.", default=None
    )


async def ordering_params(
    order_by: Optional[str] = None,
    sort_type: Optional[Literal["asc", "desc"]] = "desc",
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> OrderingFilter:
    return OrderingFilter(
        order_by=order_by, sort_type=sort_type, limit=limit, offset=offset
    )


async def time_params(date_from: Optional[date] = None, date_to: Optional[date] = None):
    return DateRangeFilter(date_from=date_from, date_to=date_to)


async def pagination_param(paginate: bool = False) -> bool:
    return paginate


OrderingDep = Annotated[OrderingFilter, Depends(ordering_params)]
DateRangeDep = Annotated[DateRangeFilter, Depends(time_params)]
PaginateDep = Annotated[bool, Depends(pagination_param)]
