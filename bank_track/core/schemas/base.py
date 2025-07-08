from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseDomainModel(BaseModel):
    id: str | UUID


class TimestampMixin(BaseModel):
    created_at: datetime
    last_modified: datetime
