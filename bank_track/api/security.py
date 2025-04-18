import requests
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt

from bank_track.api.conf import Settings
from bank_track.api.database import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security = HTTPBearer()


def get_clerk_public_key(
    settings: Settings = Depends(get_settings),
) -> list[dict[str, str]]:
    """Retrieves the public keys from Clerk.

    Raises:
        HTTPException: If no keys are found from Clerk, an exception is raised.
    """
    headers = {"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
    response = requests.get("https://api.clerk.dev/v1/jwks", headers=headers)

    if not response.ok:
        response.raise_for_status()

    jwks: dict = response.json()
    if jwks.get("keys"):
        return jwks["keys"]
    raise HTTPException(status_code=404, detail="No keys found in the JWKS")


def validate_clerk_token(
    token: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate the JWT token from Clerk provider.

    Args:
        token (HTTPAuthorizationCredentials): Do not use directly. Handled by the FastAPI dependency injection system.

    Raises:
        HTTPException: An exception is raised when the validation of the token is not successful.
    """
    try:
        jwks = get_clerk_public_key()
        payload = jwt.decode(
            token.credentials,
            jwks[0],
            algorithms=["RS256"],
            options={"verify_exp": False},
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_id(token_payload: dict = Depends(validate_clerk_token)) -> str:
    """Retrieves the user ID from the JWT payload.

    Args:
        token_payload (dict): The token to validate. Defaults to Depends(validate_clerk_token), managed by the FastAPI dependency injection system.

    Raises:
        HTTPException: Raised when if the `sub` entry evaluates to `False` in the `token_payload`.
    """
    if user_id := token_payload.get("sub"):
        return user_id

    raise HTTPException(
        status_code=401, detail="Invalid token - Impossible to retrieve the user ID"
    )
