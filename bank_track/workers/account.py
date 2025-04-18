from typing import Type

from sqlalchemy.orm import Session

from bank_track.core.adapters import AccountSQLService
from bank_track.core.models.accounts import AccountCreate
from bank_track.workers.base import Worker, log_worker


class AccountWorker(Worker[AccountCreate, AccountSQLService]):
    ENDPOINT_TPL = (
        "https://bankaccountdata.gocardless.com/api/v2/accounts/{provider_id}/details/"
    )

    def __init__(
        self,
        access_token: str,
        model: Type[AccountCreate],
        sql_session: Session,
        service: Type[AccountSQLService],
        endpoint_params: dict,
        account_id: str,
        user_id: str,
    ) -> None:
        super().__init__(access_token, model, sql_session, service, endpoint_params)
        self.account_id = account_id
        self.user_id = user_id

    @log_worker
    def format(self) -> None:
        detail: dict[str, str] = self._raw_data.get("account", {})

        self._data = [
            self.model(
                **{
                    "account_id": self.account_id,
                    "provider_id": detail["resourceId"],
                    "iban": detail["iban"],
                    "currency": detail["currency"],
                    "product": detail["product"],
                    "account_type": detail["cashAccountType"],
                    "linked_account": detail.get("linkedAccounts"),
                    "usage": detail.get("usage", "PRIV"),
                    "user_id": self.user_id,
                    "access": True,
                }
            )
        ]
