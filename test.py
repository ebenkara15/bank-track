import asyncio

from bank_track.api.database import get_settings
from bank_track.core.schemas.balances import BalanceCreate
from bank_track.core.schemas.transactions import TransactionCreate
from bank_track.infra.bank import GoCardlessTokenManager
from bank_track.infra.db import Database
from bank_track.services.crud import BalanceSQLService, TransactionSQLService

PROVIDER_IDS = [
    "44014b00-ad9e-49dd-8f95-a27570f73d9f",
    "2a3bf6ff-5d91-4f1f-bb7b-e5140649a019",
]
ACCOUNT_IDS = [
    "Q0FSRF81MDAxNTM3MDUxOVg3NTQ",
    "QUNDT1VOVF8wMTAxNzA4MjI1NVA",
]
# ACCOUNT_IDS = [
#     "54f3b84f-0df1-4ddc-bb63-4797017a8bf3",
# ]


# def create_db_and_tables():
#     engine = get_engine()

#     # BaseSQLModel.metadata.drop_all(engine)
#     BaseSQLModel.metadata.create_all(engine)

#     return engine


# engine = create_db_and_tables()
# session = Session(engine)


# # Create a User
# user = UserSQL(user_id="user_2beBRbftCVlzLy99xiHItXarTKF")
# session.add(user)
# session.commit()
# session.refresh(user)

# # Create an Account
# for account_id in ACCOUNT_IDS:
#     try:
#         account = AccountSQL(
#             **{
#                 "account_id": account_id,
#                 "iban": "FR9430002010170000082255P21",
#                 "name": "Compte de dépôts",
#                 "currency": "EUR",
#                 "product": "Compte de dépôts",
#                 "account_type": "CACC",
#                 "linked_account": "01017082255P",
#                 "usage": "PRIV",
#                 "user_id": user.user_id,
#             }
#         )
#         session.add(account)
#         session.commit()
#     except Exception as e:
#         continue


# # Create some ExpenseCategories
# category_food = ExpenseCategorySQL(
#     **{
#         "category_name": "Food",
#         "category_description": "Food expenses such as groceries, restaurants, etc.",
#     }
# )
# category_transport = ExpenseCategorySQL(
#     **{
#         "category_name": "Transport",
#         "category_description": "Transportation expenses such as bus, train, taxi, etc.",
#     }
# )
# session.add(category_food)
# session.add(category_transport)
# session.commit()

# # Create a Balance
# balance = BalanceSQL(
#     **{
#         "amount": 7128.03,
#         "currency": "EUR",
#         "reference_date": "2021-01-12",
#         "balance_type": "closingBooked",
#         "account_id": "2a3bf6ff-5d91-4f1f-bb7b-e5140649a019",
#     }
# )
# session.add(balance)
# session.commit()

# balance_2 = BalanceSQL(
#     **{
#         "amount": 7038.89,
#         "currency": "EUR",
#         "reference_date": "2021-01-15",
#         "balance_type": "expected",
#         "account_id": "2a3bf6ff-5d91-4f1f-bb7b-e5140649a019",
#     }
# )
# balance_3 = BalanceSQL(
#     **{
#         "amount": 6998.46,
#         "currency": "EUR",
#         "reference_date": "2021-01-16",
#         "balance_type": "expected",
#         "account_id": "2a3bf6ff-5d91-4f1f-bb7b-e5140649a019",
#     }
# )
# session.merge(balance_2)
# session.merge(balance_3)
# session.commit()

# # Create a Transaction
# transaction = TransactionSQL(
#     **{
#         "transaction_id": "9e6b98c7-7cc2-4e5e-9f0d-96f665266576",
#         "amount": -12.03,
#         "currency": "EUR",
#         "booking_date": "2021-01-12",
#         "value_date": "2021-01-12",
#         "account_id": "2a3bf6ff-5d91-4f1f-bb7b-e5140649a019",
#         "categories": [category_food],
#     }
# )
# session.add(transaction)
# session.commit()
# transaction_modified = TransactionSQL(
#     **{
#         "transaction_id": "9e6b98c7-7cc2-4e5e-9f0d-96f665266576",
#         "amount": "-12.13",
#         "currency": "EUR",
#         "booking_date": "2021-01-15",
#         "value_date": "2021-01-12",
#         "account_id": "2a3bf6ff-5d91-4f1f-bb7b-e5140649a019",
#         "categories": [category_food],
#     }
# )
# session.merge(transaction_modified)
# session.commit()


if __name__ == "__main__":

    async def main():
        from bank_track.workers import BalanceWorker, TransactionWorker

        settings = get_settings()

        token_mgr = GoCardlessTokenManager(
            secret_id=settings.GOC_SECRET_ID, secret_key=settings.GOC_SECRET_KEY
        )
        ACCESS_TOKEN = await token_mgr.get_token()
        db = Database(settings=settings)
        session = await anext(db.get_session())

        tasks = []

        for account_id, provider_id in zip(ACCOUNT_IDS, PROVIDER_IDS):
            txn_worker = TransactionWorker(
                access_token=ACCESS_TOKEN,
                model=TransactionCreate,
                sql_session=session,
                service=TransactionSQLService,
                endpoint_params={"provider_id": provider_id},
                account_id=account_id,
                user_id="user_2beBRbftCVlzLy99xiHItXarTKF",
            )

            blc_worker = BalanceWorker(
                access_token=ACCESS_TOKEN,
                model=BalanceCreate,
                sql_session=session,
                service=BalanceSQLService,
                endpoint_params={"provider_id": provider_id},
                account_id=account_id,
                user_id="user_2beBRbftCVlzLy99xiHItXarTKF",
            )

            tasks += [txn_worker.run(), blc_worker.run()]

        await asyncio.gather(*tasks)
        await session.close_all()

    asyncio.run(main=main())

    print("Dummy")
