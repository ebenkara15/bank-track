from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, ClassVar, Generic, List, Type, TypeVar

import requests
from loguru import logger as logging
from sqlalchemy.orm import Session

from bank_track.core.adapters import BaseSQLService
from bank_track.core.models.base import BaseDomainModel
from bank_track.workers.errors import GoCardlessExceptionHandler


def log_worker(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Starting {func.__name__}")
        func(*args, **kwargs)
        logging.success(f"Finished {func.__name__}")

    return wrapper


class BaseWorker(ABC):
    ENDPOINT: ClassVar[str]

    @abstractmethod
    @log_worker
    def fetch(self) -> None:
        ...

    @abstractmethod
    @log_worker
    def format(self) -> None:
        ...

    @abstractmethod
    @log_worker
    def save(self) -> None:
        ...

    @abstractmethod
    def run(self) -> None:
        ...


M = TypeVar("M", bound=BaseDomainModel)
S = TypeVar("S", bound=BaseSQLService)


class Worker(Generic[M, S], BaseWorker):
    ENDPOINT_TPL: str

    def __init__(
        self,
        access_token: str,
        model: Type[M],
        sql_session: Session,
        service: Type[S],
        endpoint_params: dict,
    ) -> None:
        self.access_token = access_token
        self.model = model
        self.svc = service(sql_session)

        if endpoint_params:
            self.endpoint_params = endpoint_params
            self.endpoint = self.ENDPOINT_TPL.format(**self.endpoint_params)
        else:
            self.endpoint = self.ENDPOINT_TPL

        # Internal only
        self._raw_data: dict[str, Any] = {}
        self._data: List[M] = []

    @log_worker
    def fetch(self) -> None:
        """Fetch data from the GoCardless API.

        Returns nothing but update the `self._data` variable.
        """
        response = requests.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        if not response.ok:
            error_details = response.json()
            logging.error(f"Failed to fetch data. {error_details['detail']}")
            GoCardlessExceptionHandler.handle(error_details)

        logging.info(f"Successfully fetched {self.model.__name__}")
        self._raw_data = response.json()

    @log_worker
    def format(self) -> None:
        raise NotImplementedError

    @log_worker
    def save(self) -> None:
        logging.info(f"Saving {len(self._data)} {self.model.__name__}")
        for d in self._data:
            try:
                self.svc.upsert(d)  # type: ignore
            except Exception as e:
                logging.exception(f"Error while saving {self.model.__name__}")
                raise e

    def run(self) -> None:
        self.fetch()
        self.format()
        self.save()
