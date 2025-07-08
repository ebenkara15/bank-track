from dagster import asset

from bank_track.api.database import get_session
from bank_track.core.schemas import TransactionCreate
from bank_track.infra.bank import GoCardlessTokenManager
from bank_track.services.crud import TransactionSQLService
from bank_track.workers import TransactionWorker


@asset
def fetch_transactions():
    API_KEYS = {
        "secret_id": "ceeeabc1-5e3c-43fb-a0cb-db00c1d5873a",
        "secret_key": "8d4f605b58c8aeb9a79085aa15981c3888799e7f55974a72b7f7d7c07aa3091114e9101a1a39a38bd0af3d7d8a5f55db7cd541f5b148bdab63888bd6f20e3049",
    }
    ACCOUNT_IDS = [
        "9db37e15-a2bf-46be-932b-0e0ec7b336f8",
        "2a3bf6ff-5d91-4f1f-bb7b-e5140649a019",
    ]

    session = next(get_session())
    token_mgr = GoCardlessTokenManager(**API_KEYS)
    token = token_mgr.get_token()["access"]

    for account_id in ACCOUNT_IDS:
        txn_worker = TransactionWorker(
            access_token=token,
            model=TransactionCreate,
            sql_session=session,
            service=TransactionSQLService,
            endpoint_params={"account_id": account_id},
        )

        txn_worker.run()
