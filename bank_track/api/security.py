from typing import Optional
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt

from bank_track.api.conf import Settings
from bank_track.api.database import get_settings
from bank_track.services.crud import BaseSQLService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security = HTTPBearer()


async def get_clerk_public_key(
    settings: Settings = get_settings(),
) -> list[dict[str, str]]:
    """Retrieves the public keys from Clerk.

    Raises:
        HTTPException: If no keys are found from Clerk, an exception is raised.
    """
    headers = {"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}

    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        response = await client.get("https://api.clerk.dev/v1/jwks", headers=headers)

    if not response.status_code < 400:
        response.raise_for_status()

    jwks: dict = response.json()
    if jwks.get("keys"):
        return jwks["keys"]

    raise HTTPException(status_code=401, detail="No keys found in the JWKS.")


async def validate_clerk_token(
    token: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate the JWT token from Clerk provider.

    Args:
        token (HTTPAuthorizationCredentials): Do not use directly. Handled by the FastAPI dependency injection system.

    Raises:
        HTTPException: An exception is raised when the validation of the token is not successful.
    """
    try:
        jwks = await get_clerk_public_key()
        payload = jwt.decode(
            token.credentials,
            jwks[0],
            algorithms=["RS256"],
            options={"verify_exp": False},
        )
        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_user_id(token_payload: dict = Depends(validate_clerk_token)) -> str:
    """Retrieves the user ID from the JWT payload.

    Args:
        token_payload (dict): The token to validate. Defaults to Depends(validate_clerk_token), managed by the FastAPI dependency injection system.

    Raises:
        HTTPException: Raised when the `sub` entry evaluates to `False` in the `token_payload`.
    """
    if user_id := token_payload.get("sub"):
        return user_id

    raise HTTPException(
        status_code=401, detail="Invalid token - Impossible to retrieve the user ID."
    )


async def check_ownership(
    svc: BaseSQLService,
    resource_id: str | UUID | list[str] | list[UUID],
    user_id: str,
    account_id: Optional[str] = None,
) -> bool:
    if account_id:
        db_obj = await svc.get_by(id=resource_id, user_id=user_id, account_id=account_id)
    else:
        db_obj = await svc.get_by(id=resource_id, user_id=user_id)

    if not db_obj:
        raise HTTPException(status_code=404, detail="Resource not found.")

    return True
