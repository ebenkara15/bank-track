from decimal import Decimal

from pydantic import BaseModel

from bank_track.api.query import DateGroup


class DateGroupedAggregation(BaseModel):
    date_group: DateGroup


class SpendingByCategory(BaseModel):
    category_name: str
    amount: Decimal
