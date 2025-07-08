from typing import Type

import pytest
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class DummyModel(Base):
    __tablename__ = "dummy"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    amount: Mapped[int] = mapped_column(Integer)
    value_type: Mapped[str] = mapped_column(String)


@pytest.fixture
def model() -> Type[DummyModel]:
    return DummyModel
