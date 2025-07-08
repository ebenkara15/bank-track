import httpx
from pydantic import BaseModel


class GoCardlessToken(BaseModel):
    """A base class representing a GoCardless token."""

    access: str
    access_expires: int
    refresh: str
    refresh_expires: int


class GoCardlessTokenManager:
    """Manages the GoCardless API token

    It is a simple class that manages the GoCardless API token.
    It can renew the token but not refresh it for now.

    Attributes:
        secret_id (str): the secret ID for the GoCardless API
        secret_key (str): the secret key for the GoCardless API
        token (GoCardlessToken): the token object containing the access and refresh tokens
    """

    BASE_ENDPOINT = "https://bankaccountdata.gocardless.com/api/v2"

    def __init__(self, secret_id: str, secret_key: str) -> None:
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        self.__secret_id = secret_id
        self.__secret_key = secret_key
        self.token: GoCardlessToken | None = None
        # TODO: add support for refresh token

    def _renew_token(self) -> GoCardlessToken:
        """Renew the GoCardless API token"""

        url = f"{self.BASE_ENDPOINT}/token/new/"
        data = {"secret_id": self.__secret_id, "secret_key": self.__secret_key}

        with httpx.Client(follow_redirects=True, timeout=10) as client:
            response = client.post(url, headers=self.headers, json=data)

        if not response.status_code < 400:
            response.raise_for_status()

        return GoCardlessToken(**response.json())

    def _refresh_token(self) -> dict:
        raise NotImplementedError

    def get_token(self) -> str:
        """Returns a new GoCardless API token."""
        if not self.token:
            self.token = self._renew_token()
        return self.token.access


class GoCardlessClient:
    """A client to interact with GoCardless services. Mostly used to create accounts and requisitions.

    Please refer to the [GoCardless Bank Account data service documentation](https://developer.gocardless.com/bank-account-data/overview).
    """

    BASE_ENDPOINT = "https://bankaccountdata.gocardless.com/api/v2"

    def __init__(self, token_manager: GoCardlessTokenManager) -> None:
        self.token_manager = token_manager
        self.redirect_url = "http://localhost:5173/accounts/verify"
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token_manager.get_token()}",
        }
        self._client = httpx.AsyncClient(follow_redirects=True, timeout=10)

    async def get_institutions_by_country(self, country: str) -> list:
        """Returns all the institutions for given a country.

        Args:
            country (str): An ISO Alpha-2 country code.

        Returns:
            list: List of institutions for the given country.

        Example:
            ```
            >>> await client.get_institutions_by_country(country="US")
            >>> await client.get_institutions_by_country(country="FR")
            >>> await client.get_institutions_by_country(country="de")
            ```
        """
        response = await self._client.get(
            f"{self.BASE_ENDPOINT}/institutions/",
            headers=self.headers,
            params={"country": country.lower()},
        )
        if not response.status_code < 400:
            response.raise_for_status()

        return response.json()

    async def get_institution_by_id(self, institution_id: str) -> dict:
        """Return instutition details for a given institution ID.

        Args:
            institution_id (str): The institution ID. Find the list on Go Cardlesss website or see the result of the `get_institutions_by_country` function.

        Returns:
            dict: The institution details.
        """
        response = await self._client.get(
            f"{self.BASE_ENDPOINT}/institutions/{institution_id}",
            headers=self.headers,
        )
        if not response.status_code < 400:
            response.raise_for_status()

        return response.json()

    async def create_agreement(self, institution_id: str) -> dict:
        """Create a new agreement.

        Args:
            institution_id (str): The institution ID.

        Returns:
            dict: The agreement for the given institution.
        """
        response = await self._client.post(
            f"{self.BASE_ENDPOINT}/agreements/enduser/",
            headers=self.headers,
            data={
                "institution_id": institution_id,
                "max_historical_days": 90,
                "access_valid_for_days": 180,
            },
        )
        if not response.status_code < 400:
            response.raise_for_status()

        return response.json()

    async def create_requisition(self, institution_id: str, agreement_id: str) -> dict:
        """Generate a new agreement that must be accepted by the enduser.

        Args:
            institution_id (str): The institution ID.
            agreement_id (str): The agreement ID.

        Returns:
            dict: The requisition for the given institution ID and agreement ID.
        """
        response = await self._client.post(
            f"{self.BASE_ENDPOINT}/requisitions/",
            headers=self.headers,
            data={
                "institution_id": institution_id,
                "agreement": agreement_id,
                "redirect": self.redirect_url,
            },
        )
        if not response.status_code < 400:
            response.raise_for_status()

        return response.json()

    async def get_requisition(self, requisition_id: str) -> dict:
        """Returns the requisition details.

        Args:
            requisition_id (str): The requisition ID.

        Returns:
            dict: The requisition details.
        """
        response = await self._client.get(
            f"{self.BASE_ENDPOINT}/requisitions/{requisition_id}",
            headers=self.headers,
        )
        if not response.status_code < 400:
            response.raise_for_status()

        data = response.json()
        return data["accounts"]

    async def get_account_detail(self, account_id) -> dict:
        """Returns account details for the given account.

        Args:
            account_id (_type_): The account ID.

        Returns:
            dict: The account details.
        """
        response = await self._client.get(
            f"{self.BASE_ENDPOINT}/accounts/{account_id}/details/",
            headers=self.headers,
        )
        if not response.status_code < 400:
            response.raise_for_status()

        account = response.json()
        return account["account"]
