from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMetadata(BaseModel):
    limit: int = Field(
        description="The maximum number of items to be returned.", le=100
    )
    offset: int = Field(description="The offset used to retrieved the items.", ge=0)
    count: int = Field(description="The number of items retrieved.", ge=0)
    total: int = Field(description="The total number of items found in DB.", ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    data: Optional[list[T]] = None
    pagination: PaginationMetadata
