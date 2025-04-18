from functools import lru_cache
from typing import Callable, Generator, Type, TypeVar

from fastapi import Depends
from sqlalchemy.orm import Session

from bank_track.api.conf import Settings
from bank_track.core.adapters import BaseSQLService
from bank_track.infra.db import Database


@lru_cache
def get_settings() -> Settings:
    """Returns the settings read from the environment.

    Returns:
        Settings: The pydantic.BaseSettings class that contains secrets and variables for the app.
    """
    return Settings()


@lru_cache
def get_db() -> Database:
    """Returns a Database instance. Mostly use as a dependency.

    Returns:
        Database: The Database instannce.

    See also:
        [infra.db.Database](./infra/db)
    """
    return Database(settings=get_settings())


def get_session(db: Database = Depends(get_db)) -> Generator[Session, None, None]:
    """Yields a new database session. Mostly use as a dependency.

    Args:
        db (Database): The Database instance to use. Managed by the FastAPI dependency injection system.

    Yields:
        Generator[Session, None, None]: The new database session.
    """
    yield from db.get_session()


T = TypeVar("T", bound=BaseSQLService)


def get_service(service_cls: Type[T]) -> Callable[[Session], T]:
    """Returns a new instance of the service class specified initiated with a database session.

    Args:
        service_cls (Type[T]): A BaseSQLService class to instantiate.

    Returns:
        Callable[[Session], T]: A new instance.
    """

    def _get_service(session: Session = Depends(get_session)) -> T:
        return service_cls(sql_session=session)

    return _get_service
