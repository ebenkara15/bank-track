from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from bank_track.core.schemas.transactions import TransactionCreate
from bank_track.services.crud import TransactionSQLService
from bank_track.workers.base import Worker, log_worker


class TransactionWorker(Worker[TransactionCreate, TransactionSQLService]):
    ENDPOINT_TPL = "https://bankaccountdata.gocardless.com/api/v2/accounts/{provider_id}/transactions/"

    def __init__(
        self,
        access_token: str,
        model: Type[TransactionCreate],
        sql_session: AsyncSession,
        service: Type[TransactionSQLService],
        endpoint_params: dict,
        account_id: str,
        user_id: str,
    ) -> None:
        super().__init__(access_token, model, sql_session, service, endpoint_params)
        self.account_id = account_id
        self.user_id = user_id

    @log_worker
    async def format(self) -> None:
        booked_txns = self._format_booked_transactions(
            self._raw_data["transactions"].get("booked", [])
        )
        pending_txns = self._format_pending_transactions(
            self._raw_data["transactions"].get("pending", [])
        )

        self._data = [*booked_txns, *pending_txns]  # type: ignore

    def _format_booked_transactions(
        self, booked_txns: list[dict]
    ) -> list[TransactionCreate]:
        formatted_txns = []
        for txn in booked_txns:
            formatted_txns.append(
                self.model(
                    **{
                        "transaction_id": txn["transactionId"],
                        "amount": txn["transactionAmount"]["amount"],
                        "currency": txn["transactionAmount"]["currency"],
                        "booking_date": txn["bookingDate"],
                        "value_date": txn["valueDate"],
                        "transaction_type": "booked",
                        "account_id": self.account_id,
                        "user_id": self.user_id,
                    }
                )
            )

        return formatted_txns

    def _format_pending_transactions(
        self, pending_txns: list[dict]
    ) -> list[TransactionCreate]:
        formatted_txns = []
        for txn in pending_txns:
            formatted_txns.append(
                self.model(
                    **{
                        "transaction_id": txn["transactionId"],
                        "amount": txn["transactionAmount"]["amount"],
                        "currency": txn["transactionAmount"]["currency"],
                        "booking_date": txn["bookingDate"],
                        "value_date": txn["valueDate"],
                        "transaction_type": "pending",
                        "account_id": self.account_id,
                        "user_id": self.user_id,
                    }
                )
            )

        return formatted_txns
