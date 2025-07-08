from functools import lru_cache
from typing import AsyncGenerator, Callable, Type, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bank_track.api.conf import Settings
from bank_track.infra.db import Database
from bank_track.services.crud import BaseSQLService


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


async def get_session(
    db: Database = Depends(get_db),
) -> AsyncGenerator[AsyncSession, None]:
    """Yields a new database session. Mostly use as a dependency.

    Args:
        db (Database): The Database instance to use. Managed by the FastAPI dependency injection system.

    Yields:
        Generator[Session, None, None]: The new database session.
    """
    async for session in db.get_session():
        yield session


T = TypeVar("T", bound=BaseSQLService)


def get_service(service_cls: Type[T]) -> Callable[[AsyncSession], T]:
    """Returns a new instance of the service class specified initiated with a database session.

    Args:
        service_cls (Type[T]): A BaseSQLService class to instantiate.

    Returns:
        Callable[[Session], T]: A new instance.
    """

    def _get_service(session: AsyncSession = Depends(get_session)) -> T:
        return service_cls(session=session)

    return _get_service
