from fastapi import Depends, HTTPException, Response
from fastapi.routing import APIRouter
from loguru import logger
from pydantic_extra_types.country import CountryAlpha2

from bank_track.api.database import get_service
from bank_track.api.security import get_user_id
from bank_track.core.adapters import AccountSQLService, RequisitionSQLService
from bank_track.core.models.accounts import AccountCreate, AccountRead
from bank_track.core.models.users import AccountsRequisition
from bank_track.infra.bank import GoCardlessClient, GoCardlessTokenManager

router = APIRouter(prefix="/accounts", tags=["accounts"])


API_KEYS = {
    "secret_id": "ceeeabc1-5e3c-43fb-a0cb-db00c1d5873a",
    "secret_key": "8d4f605b58c8aeb9a79085aa15981c3888799e7f55974a72b7f7d7c07aa3091114e9101a1a39a38bd0af3d7d8a5f55db7cd541f5b148bdab63888bd6f20e3049",
}

token_mgr = GoCardlessTokenManager(**API_KEYS)
client = GoCardlessClient(token_manager=token_mgr)


@router.get("/institutions/{country}")
def get_institutions(country: CountryAlpha2) -> list[dict]:
    if country:
        return client.get_institutions_by_country(country=country)
    raise HTTPException(status_code=404, detail="Country not found")


@router.post("/{institution_id}/agreement")
def create_agreement(
    institution_id: str,
    svc: RequisitionSQLService = Depends(get_service(RequisitionSQLService)),
    user_id: str = Depends(get_user_id),
) -> dict:
    if institution_id:
        # TODO:  Store the agreement in the database
        agreement = client.create_agreement(institution_id)
        agreement_id = agreement["id"]
        requisition = client.create_requisition(institution_id, agreement_id)

        req = AccountsRequisition(
            user_id=user_id,
            requisition_id=requisition["id"],
            institution_id=institution_id,
            agreement_id=agreement_id,
        )
        svc.create(req)
        return requisition

    raise HTTPException(status_code=404, detail="Institution not found")


@router.post("/requisition/accept/{ref}")
def create_requisition(
    ref: str,
    requisition_svc: RequisitionSQLService = Depends(get_service(RequisitionSQLService)),
    account_svc: AccountSQLService = Depends(get_service(AccountSQLService)),
    user_id: str = Depends(get_user_id),
) -> Response:
    logger.info(f"Requisition ref: {ref}")

    if ref:
        req = requisition_svc.get_by(user_id=user_id, requisition_id=ref)
        if req:
            req.accepted = True
            requisition_svc.update(req)
            account_ids = client.get_requisition(requisition_id=ref)

            for account_id in account_ids:
                account_data = client.get_account_detail(account_id)
                account = AccountCreate(
                    provider_id=account_id,
                    account_id=account_data.get("resourceId"),
                    user_id=user_id,
                    iban=account_data.get("iban"),
                    name=account_data.get("name"),
                    currency=account_data.get("currency"),
                    product=account_data.get("product"),
                    account_type=account_data.get("cashAccountType"),
                    linked_account=account_data.get("linkedAccounts"),
                    usage=account_data.get("usage", "PRIV"),
                    access=True,
                )
                account_svc.create(account)
            return Response(status_code=200)
    raise HTTPException(status_code=404, detail="Requisition not found")


@router.get("/{account_id}")
def get_account(
    account_id: str,
    svc: AccountSQLService = Depends(get_service(AccountSQLService)),
    user_id: str = Depends(get_user_id),
) -> AccountRead | None:
    if user_id:
        return svc.get_by(user_id=user_id, account_id=account_id)
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/")
def get_user_accounts(
    svc: AccountSQLService = Depends(get_service(AccountSQLService)),
    user_id=Depends(get_user_id),
) -> list[AccountRead] | AccountRead | None:
    if user_id:
        accounts = svc.list_by(user_id=user_id)
        return accounts
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/")
def create_account(
    account: AccountCreate,
    svc: AccountSQLService = Depends(get_service(AccountSQLService)),
    user_id: str = Depends(get_user_id),
) -> AccountRead:
    if account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        return svc.create(account)
