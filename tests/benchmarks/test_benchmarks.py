from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import Select

from bank_track.api.query import DateRangeFilter, OrderingFilter
from bank_track.core.models.sql import TransactionSQL
from bank_track.core.schemas.balances import Balance, BalanceCreate
from bank_track.core.schemas.categories import ExpenseCategory, ExpenseCategoryCreate
from bank_track.core.schemas.transactions import Transaction, TransactionCreate
from bank_track.core.schemas.types import BalanceType, CurrencyType
from bank_track.services.filtering import QueryFilter, build_statement


# -- Schema validation benchmarks --


@pytest.mark.benchmark
def test_transaction_schema_creation():
    """Benchmark creating a Transaction schema instance."""
    Transaction(
        transaction_id=str(uuid4()),
        amount=Decimal("-42.50"),
        currency=CurrencyType.EUR,
        booking_date=date(2024, 1, 15),
        value_date=date(2024, 1, 15),
        transaction_type="booked",
    )


@pytest.mark.benchmark
def test_transaction_create_schema_validation():
    """Benchmark creating a TransactionCreate with full validation."""
    TransactionCreate(
        transaction_id=str(uuid4()),
        amount=Decimal("-99.99"),
        currency=CurrencyType.USD,
        booking_date=date(2024, 6, 1),
        value_date=date(2024, 6, 1),
        transaction_type="pending",
        account_id="test-account-001",
        user_id="user_abcdefghijklmnopqrstuvwxyza",
    )


@pytest.mark.benchmark
def test_balance_schema_creation():
    """Benchmark creating a Balance schema instance."""
    Balance(
        amount=Decimal("5000.00"),
        currency=CurrencyType.EUR,
        reference_date=date(2024, 3, 1),
        balance_type=BalanceType.CLOSING_BOOKED,
    )


@pytest.mark.benchmark
def test_balance_create_schema_validation():
    """Benchmark creating a BalanceCreate with full validation."""
    BalanceCreate(
        amount=Decimal("12345.67"),
        currency=CurrencyType.GBP,
        reference_date=date(2024, 7, 15),
        balance_type=BalanceType.EXPECTED,
        account_id="test-account-002",
        user_id="user_abcdefghijklmnopqrstuvwxyza",
    )


@pytest.mark.benchmark
def test_expense_category_schema_creation():
    """Benchmark creating an ExpenseCategory schema instance."""
    ExpenseCategory(
        category_name="Groceries",
        category_description="Weekly grocery shopping expenses",
    )


@pytest.mark.benchmark
def test_expense_category_create_schema_validation():
    """Benchmark creating an ExpenseCategoryCreate with validation."""
    ExpenseCategoryCreate(
        category_name="Transport",
        category_description="Public transport and taxi expenses",
        user_id="user_abcdefghijklmnopqrstuvwxyza",
    )


# -- Query filter benchmarks --


@pytest.mark.benchmark
def test_parse_filters_equality():
    """Benchmark parsing simple equality filters."""
    QueryFilter.parse_filters(
        TransactionSQL,
        account_id="test-account-001",
        currency="EUR",
    )


@pytest.mark.benchmark
def test_parse_filters_in_list():
    """Benchmark parsing an IN-list filter."""
    QueryFilter.parse_filters(
        TransactionSQL,
        account_id=["account-001", "account-002", "account-003"],
    )


@pytest.mark.benchmark
def test_parse_filters_comparison_operators():
    """Benchmark parsing filters with comparison operators."""
    QueryFilter.parse_filters(
        TransactionSQL,
        amount__gte=100,
        amount__lte=5000,
        booking_date__gt=date(2024, 1, 1),
    )


@pytest.mark.benchmark
def test_parse_filters_between():
    """Benchmark parsing a BETWEEN filter."""
    QueryFilter.parse_filters(
        TransactionSQL,
        amount__btwn=[100, 5000],
    )


@pytest.mark.benchmark
def test_parse_filters_combined():
    """Benchmark parsing a combination of filter types."""
    QueryFilter.parse_filters(
        TransactionSQL,
        account_id="test-account-001",
        amount__gte=50,
        amount__lte=1000,
        currency="EUR",
    )


# -- Query ordering benchmarks --


@pytest.mark.benchmark
def test_parse_ordering_full():
    """Benchmark parsing ordering with all parameters."""
    statement = Select(TransactionSQL)
    ordering = OrderingFilter(
        order_by="created_at", sort_type="desc", limit=100, offset=50
    )
    QueryFilter.parse_ordering(
        db_model=TransactionSQL, statement=statement, ordering=ordering
    )


@pytest.mark.benchmark
def test_parse_ordering_minimal():
    """Benchmark parsing ordering with minimal parameters."""
    statement = Select(TransactionSQL)
    ordering = OrderingFilter()
    QueryFilter.parse_ordering(
        db_model=TransactionSQL, statement=statement, ordering=ordering
    )


@pytest.mark.benchmark
def test_build_statement_with_ordering():
    """Benchmark the build_statement helper with full parameters."""
    statement = Select(TransactionSQL)
    build_statement(
        statement=statement,
        limit=50,
        offset=10,
        order_by=TransactionSQL.amount,
        sort_type="desc",
    )


# -- Query param validation benchmarks --


@pytest.mark.benchmark
def test_date_range_filter_validation():
    """Benchmark DateRangeFilter creation and validation."""
    DateRangeFilter(
        date_from=date(2024, 1, 1),
        date_to=date(2024, 12, 31),
    )


@pytest.mark.benchmark
def test_ordering_filter_creation():
    """Benchmark OrderingFilter creation."""
    OrderingFilter(
        order_by="booking_date",
        sort_type="asc",
        limit=25,
        offset=0,
    )
