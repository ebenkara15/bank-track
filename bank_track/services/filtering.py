from typing import Literal, Optional, Type

from sqlalchemy import BinaryExpression, Column, Select
from sqlalchemy.orm import InstrumentedAttribute, Mapped

from bank_track.api.query import OrderingFilter
from bank_track.core.models.sql import BaseSQLModel


class QueryFilter:
    """A simple class to handle filtering of SQL models from string syntax"""

    SUPPORTED_OPERATIONS = ["gte", "gt", "lte", "lt", "ne", "btwn"]

    @classmethod
    def apply_filter(
        cls, operation: str, column: InstrumentedAttribute, value
    ) -> BinaryExpression:
        if operation not in cls.SUPPORTED_OPERATIONS:
            raise ValueError(
                f"Unsupported SQL operation. Parsed operation {operation}."
            )

        match operation:
            case "gte":
                filtr = column >= value
            case "gt":
                filtr = column > value
            case "lte":
                filtr = column <= value
            case "lt":
                filtr = column < value
            case "ne":
                filtr = column != value
            case "btwn":
                if not isinstance(value, list) or len(value) != 2:
                    raise ValueError(
                        f"For BETWEEN operator the value must be a two value list: {value}"
                    )
                cleft, cright = value
                filtr = column.between(cleft=cleft, cright=cright)

        return filtr

    @classmethod
    def parse_filters(
        cls, db_model: Type[BaseSQLModel], **kwargs
    ) -> list[BinaryExpression]:
        """Parses the filters given in `kwargs`.

        Must follow the supported operators:

        | Operator Style                    | Argument Style                 |
        | --------------------------------- | ------------------------------ |
        | `col = value`                     | `col=value`                    |
        | `col in [value_1, value_2]`       | `col=[value_1, value_2]`       |
        | `col >= value`                    | `col__gte=value`               |
        | `col > value`                     | `col__gt=value`                |
        | `col <= value`                    | `col__lte=value`               |
        | `col < value`                     | `col__lt=value`                |
        | `col != value`                    | `col__ne=value`                |
        | `col between value_1 and value_2` | `col__btwn=[value_1, value_2]` |

        Args:
            db_model (Type[BaseSQLModel]): The SQL model to apply filters to.
            kwargs: The filters to apply to the model. See the accepted format above.

        Example:
        #TODO
        """

        filters = []
        for filtr, value in kwargs.items():
            # If the condition is a simple equality (`=` or `IN` statement).
            if "__" not in filtr:
                if isinstance(value, list):
                    filters.append((getattr(db_model, filtr)).in_(value))
                else:
                    filters.append(getattr(db_model, filtr) == value)
            # For other operations.
            else:
                column_name, operation = filtr.split("__")
                column = getattr(db_model, column_name)

                filters.append(
                    cls.apply_filter(operation=operation, column=column, value=value)
                )

        return filters

    @classmethod
    def parse_ordering(
        cls, db_model: Type[BaseSQLModel], statement: Select, ordering: OrderingFilter
    ) -> Select:
        """Builds the SQL statement. It adds the `limit`, `offset`, `order by` and `sort type` to the statement.

        Args:
            db_model: The SQLAlchemy model used.
            statement: The sqlalchemy.Select statement.
            ordering (OrderingFilter): The object containing the filters to create the ordering.
        """

        if ordering.limit:
            statement = statement.limit(limit=ordering.limit)
        if ordering.offset:
            statement = statement.offset(offset=ordering.offset)
        if ordering.order_by:
            column: InstrumentedAttribute = getattr(db_model, ordering.order_by)
            statement = (
                statement.order_by(column.desc())
                if ordering.sort_type == "desc"
                else statement.order_by(column.asc())
            )

        return statement


def build_statement(
    statement: Select,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[Column | Mapped] = None,
    sort_type: Literal["asc"] | Literal["desc"] | None = "asc",
) -> Select:
    """Builds the SQL statement. It adds the `limit`, `offset`, `order by` and `sort type` to the statement.

    Args:
        statement (sqlalchemy.Select): The SQL statement.
        limit (int): The limit of the statement.
        offset (int): The offset of the statement.
        order_by (sqlalchemy.Column or sqlalchemy.orm.Mapped): The column to order by.
        sort_type (str): The sort type.
    """
    if limit:
        statement = statement.limit(limit=limit)

    if offset:
        statement.offset(offset=offset)

    if order_by:
        if sort_type == "asc":
            statement = statement.order_by(order_by.asc())
        elif sort_type == "desc":
            statement = statement.order_by(order_by.desc())

    return statement
