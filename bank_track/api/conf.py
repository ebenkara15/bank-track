from enum import StrEnum
from typing import Optional

from pydantic_settings import BaseSettings


class EnvSettings(StrEnum):
    """Enum to represent the different environments the API can run in.

    Attributes:
        local: local development environment
        dev: development environment
        production: production environment
    """

    LOCAL = "local"
    DEV = "dev"
    PRODUCTION = "production"


class Settings(BaseSettings, use_enum_values=True):
    """
    Settings for the API loaded from environment variables.

    Attributes:
        ENV ("local", "dev", "production"): the environment the API is running in
        GOC_SECRET_KEY (str): the secret key for the GoCardless API
        GOC_SECRET_ID (str): the secret ID for the GoCardless API
        CLERK_SECRET_KEY (str): the secret key for the Clerk API
        CLERK_JWKS_URL (str): the URL to retrieve the JWKS from Clerk
        DB_URL (str): the URL to connect to the database
        DB_ENGINE (str): the database engine to use
        DB_HOST (str): the database host to connect to
        DB_USER (str): the database user to connect as
        DB_PASSWORD (str): the database password to use
        DB_DATABASE (str): the database to connect to
    """

    ENV: EnvSettings = EnvSettings.DEV
    GOC_SECRET_KEY: str
    GOC_SECRET_ID: str
    CLERK_SECRET_KEY: str
    CLERK_JWKS_URL: Optional[str] = "https://api.clerk.dev/v1/jwks"
    DB_URL: Optional[str] = None
    DB_ENGINE: str
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str
