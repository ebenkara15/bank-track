import pytest
from sqlalchemy import Select

from bank_track.api.query import OrderingFilter
from bank_track.core.models.sql import TransactionSQL
from bank_track.services.filtering import QueryFilter
from tests.unit.services.conftest import DummyModel


@pytest.mark.parametrize(
    "db_model,order_by,sort_type,limit,offset",
    [
        (TransactionSQL, TransactionSQL.created_at.key, "desc", 100, 50),
        (TransactionSQL, TransactionSQL.amount.key, None, 100, 50),
        (TransactionSQL, TransactionSQL.value_date.key, "asc", None, None),
    ],
)
def test_parse_ordering(db_model, order_by, sort_type, limit, offset):
    statement = Select(db_model)
    ordering = OrderingFilter(
        order_by=order_by, sort_type=sort_type, limit=limit, offset=offset
    )

    statement_ordered = QueryFilter.parse_ordering(
        db_model=db_model, statement=statement, ordering=ordering
    )

    assert statement_ordered._limit == limit or 0
    assert statement_ordered._offset == offset or 0

    order_by_str = (
        f"{db_model.__tablename__}.{order_by} {sort_type or 'asc'}".lower()
        if order_by
        else ""
    )
    assert statement_ordered._order_by_clause.compile().string.lower() == order_by_str


def test_apply_filter_not_supported_operation():
    with pytest.raises(ValueError, match="Unsupported SQL operation"):
        QueryFilter.apply_filter(
            operation="nin", column=TransactionSQL.account_id, value="123456789"
        )


def test_apply_filter_between_unsupported_between_arg():
    with pytest.raises(
        ValueError, match="For BETWEEN operator the value must be a two value list"
    ):
        QueryFilter.apply_filter(
            operation="btwn", column=TransactionSQL.account_id, value="123456789"
        )


def test_apply_filter__gte(model: type[DummyModel]):
    filtr = QueryFilter.apply_filter(operation="gte", column=model.amount, value=10)
    expected_filtr = "dummy.amount >= 10"
    assert str(filtr.compile(compile_kwargs={"literal_binds": True})) == expected_filtr


def test_apply_filter__gt(model: type[DummyModel]):
    filtr = QueryFilter.apply_filter(operation="gt", column=model.amount, value=10)
    expected_filtr = "dummy.amount > 10"
    assert str(filtr.compile(compile_kwargs={"literal_binds": True})) == expected_filtr


def test_apply_filter__lte(model: type[DummyModel]):
    filtr = QueryFilter.apply_filter(operation="lte", column=model.amount, value=10)
    expected_filtr = "dummy.amount <= 10"
    assert str(filtr.compile(compile_kwargs={"literal_binds": True})) == expected_filtr


def test_apply_filter__lt(model: type[DummyModel]):
    filtr = QueryFilter.apply_filter(operation="lt", column=model.amount, value=10)
    expected_filtr = "dummy.amount < 10"
    assert str(filtr.compile(compile_kwargs={"literal_binds": True})) == expected_filtr


def test_apply_filter__ne(model: type[DummyModel]):
    filtr = QueryFilter.apply_filter(operation="ne", column=model.amount, value=10)
    expected_filtr = "dummy.amount != 10"
    assert str(filtr.compile(compile_kwargs={"literal_binds": True})) == expected_filtr


def test_apply_filter__btwn(model: type[DummyModel]):
    filtr = QueryFilter.apply_filter(
        operation="btwn", column=model.amount, value=[10, 20]
    )
    expected_filtr = "dummy.amount BETWEEN 10 AND 20"
    assert str(filtr.compile(compile_kwargs={"literal_binds": True})) == expected_filtr
