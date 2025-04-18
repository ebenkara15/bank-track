from typing import Type


class GoCardlessException(Exception):
    """A base class to handle GoCardless client error."""

    STATUS_CODE: int
    STATUS_NAME: str

    def __init__(self, message, detail):
        self.detail = detail
        self.message = message

        error_message = (
            f"[{self.STATUS_CODE} {self.STATUS_NAME}] {self.message}: {self.detail}"
        )

        super().__init__(error_message)


class InvalidAccountIDException(GoCardlessException):
    """Invalid account ID."""

    STATUS_CODE: int = 400
    STATUS_NAME: str = "Bad Request"


class InvalidOrExpiredTokenException(GoCardlessException):
    """Invalid or expired token."""

    STATUS_CODE: int = 401
    STATUS_NAME: str = "Unauthorized"


class IPNotWhitelistedException(GoCardlessException):
    """IP not whitelisted."""

    STATUS_CODE: int = 403
    STATUS_NAME: str = "Forbidden"


class NotFoundException(GoCardlessException):
    """Resource not found."""

    STATUS_CODE: int = 404
    STATUS_NAME: str = "Not Found"


class ResourceErrorException(GoCardlessException):
    """Resource error on provider/instituion side."""

    STATUS_CODE: int = 409
    STATUS_NAME: str = "Resource Error"


class RateLimitException(GoCardlessException):
    """Rate limit exceeded."""

    STATUS_CODE: int = 429
    STATUS_NAME: str = "Rate Limit Exceeded"


class InstitutionServiceFailException(GoCardlessException):
    """Request for resource failed on institution side."""

    STATUS_CODE: int = 500
    STATUS_NAME: str = "Institution Service Failure"


class InstitutionServiceUnavailableException(GoCardlessException):
    """Institution service unavailable."""

    STATUS_CODE: int = 503
    STATUS_NAME: str = "Institution Service Unavailable"


class GoCardlessExceptionHandler:
    """A class to handle exception from GoCardless service"""

    EXCEPTION_MAP: dict[int, Type[GoCardlessException]] = {
        400: InvalidAccountIDException,
        401: InvalidOrExpiredTokenException,
        403: IPNotWhitelistedException,
        404: NotFoundException,
        409: ResourceErrorException,
        429: RateLimitException,
        500: InstitutionServiceFailException,
        503: InstitutionServiceUnavailableException,
    }

    @classmethod
    def handle(cls, http_json_response: dict) -> None:
        status_code: int = http_json_response["status_code"]
        message = http_json_response["summary"]
        detail = http_json_response["detail"]

        Excp = cls.EXCEPTION_MAP[status_code]

        raise Excp(message=message, detail=detail)
