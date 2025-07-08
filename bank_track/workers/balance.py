from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from bank_track.core.schemas.balances import BalanceCreate
from bank_track.services.crud import BalanceSQLService
from bank_track.workers.base import Worker, log_worker


class BalanceWorker(Worker[BalanceCreate, BalanceSQLService]):
    ENDPOINT_TPL = (
        "https://bankaccountdata.gocardless.com/api/v2/accounts/{provider_id}/balances/"
    )

    def __init__(
        self,
        access_token: str,
        model: Type[BalanceCreate],
        sql_session: AsyncSession,
        service: Type[BalanceSQLService],
        endpoint_params: dict,
        account_id: str,
        user_id: str,
    ) -> None:
        super().__init__(access_token, model, sql_session, service, endpoint_params)
        self.account_id = account_id
        self.user_id = user_id

    @log_worker
    async def format(self) -> None:
        formatted_balances = []

        for balance in self._raw_data.get("balances", []):
            formatted_balances.append(
                self.model(
                    **{
                        "amount": balance["balanceAmount"]["amount"],
                        "currency": balance["balanceAmount"]["currency"],
                        "reference_date": balance["referenceDate"],
                        "balance_type": balance["balanceType"],
                        "account_id": self.account_id,
                        "user_id": self.user_id,
                    }
                )
            )

        self._data = formatted_balances
