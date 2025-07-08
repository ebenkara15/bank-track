import ssl
from typing import AsyncGenerator, Optional

from loguru import logger
from sqlalchemy import URL, MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bank_track.api.conf import Settings


class Database:
    """An abstraction to interact with the database through SQLAlchemy session/engine.

    This class is mostly used as a dependency. See the example below from *bank_track.api.database*.

    Example:
        ```
        @lru_cache
        def get_settings() -> Settings:
            return Settings()


        @lru_cache
        def get_db() -> Database:
            return Database(settings=get_settings())


        def get_session(
            db: Database = Depends(get_db),
        ) -> Generator[AsyncSession, None, None]:
            yield from db.get_session()
        ```
    """

    def __init__(self, settings: Settings, db_url: Optional[str | URL] = None) -> None:
        """Constructor of a new Database instance.

        Args:
            settings (Settings): A Settings instance holding environment variable.
            db_url (Optional[str  |  URL], optional): The URL of the database. Defaults to None.
        """
        self.db_url = db_url
        self._settings = settings
        self._engine = self._create_engine()
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def _create_engine(self) -> AsyncEngine:
        """Create a new engine. Used internally to generate sessions.

        Returns:
            Engine: A new engine object
        """
        if self.db_url:
            logger.info(f"Creating DB engine for {self.db_url}")
            return create_async_engine(self.db_url)

        ssl_context = ssl.create_default_context()
        self.db_url = URL.create(
            drivername=self._settings.DB_ENGINE,
            username=self._settings.DB_USER,
            password=self._settings.DB_PASSWORD,
            host=self._settings.DB_HOST,
            database=self._settings.DB_DATABASE,
            # query={"sslmode": "require"},
        )
        logger.info(f"Creating DB engine for {self.db_url}")
        return create_async_engine(self.db_url, connect_args={"ssl": ssl_context})

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Returns a new session object. It is designed to be used as a depenedency.

        Yields:
            Generator[Session, None, None]: The new Session object to be used to interact with the database.

        Example:
            ```
            @app.get("/{item_id}")
            def get_item(item_id: str, session: Session = Depends(db.get_session)): ...
            ```

        **See Also:**
            api.database.get_session()
        """
        async with self._session_factory() as db:
            yield db

    async def drop_schema(self, metadata: MetaData) -> None:
        """Drop every table declared from the MetaData in the target database.

        Args:
            metadata (MetaData): The MetaData collection of table.
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)

    async def init_schema(self, metadata: MetaData) -> None:
        """Create all tables declared from the MetaData in the target database.

        It won't recreate tables if the table already exists. Even if the table definition has changes (column addition, change of type, etc.)

        Args:
            metadata (MetaData): The table collection.
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory
