from functools import wraps
from typing import Callable

from fastapi import HTTPException


class OwnershipError(Exception):
    """Raised when a user tries to access a resource he doesn't own."""


class ResourceNotFoundError(Exception):
    """Raised when a resource is not found in the database"""


def raise_on_no_return(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)

        if not res:
            raise HTTPException(status_code=404, detail="No resource found.")
        else:
            return res

    return wrapper
