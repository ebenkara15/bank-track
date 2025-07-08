from typing import Annotated

from fastapi import Depends, HTTPException, Response
from fastapi.routing import APIRouter
from loguru import logger
from pydantic_extra_types.country import CountryAlpha2

from bank_track.api.database import get_service, get_settings
from bank_track.api.page import PaginatedResponse
from bank_track.api.query import OrderingDep, PaginateDep
from bank_track.api.security import get_user_id
from bank_track.core.schemas.accounts import AccountCreate, AccountRead
from bank_track.core.schemas.users import AccountsRequisition
from bank_track.infra.bank import GoCardlessClient, GoCardlessTokenManager
from bank_track.services.crud import AccountSQLService, RequisitionSQLService

router = APIRouter(prefix="/accounts", tags=["accounts"])


settings = get_settings()

API_KEYS = {
    "secret_id": settings.GOC_SECRET_ID,
    "secret_key": settings.GOC_SECRET_KEY,
}
token_mgr = GoCardlessTokenManager(**API_KEYS)
client = GoCardlessClient(token_manager=token_mgr)


@router.get(
    "/institutions/{country}", description="Get the institution for a given `country`."
)
async def get_institutions(country: CountryAlpha2) -> list[dict]:
    if country:
        return await client.get_institutions_by_country(country=country)
    raise HTTPException(status_code=404, detail="Country not found")


@router.post(
    "/{institution_id}/agreement",
    description="Create a new agreement given an `institution_id` for the connect user.",
)
async def create_agreement(
    institution_id: str,
    svc: Annotated[RequisitionSQLService, Depends(get_service(RequisitionSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
) -> dict:
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    if institution_id:
        # TODO:  Store the agreement in the database
        agreement = await client.create_agreement(institution_id)
        agreement_id = agreement["id"]
        requisition = await client.create_requisition(institution_id, agreement_id)

        req = AccountsRequisition(
            user_id=user_id,
            requisition_id=requisition["id"],
            institution_id=institution_id,
            agreement_id=agreement_id,
        )
        await svc.create(req)
        return requisition

    raise HTTPException(status_code=404, detail="Institution not found")


@router.post(
    "/requisition/accept/{requisition_id}",
    description="Create a new requistion given the `agreement_id` for the connected user",
)
async def create_requisition(
    requisition_id: str,
    requisition_svc: Annotated[
        RequisitionSQLService, Depends(get_service(RequisitionSQLService))
    ],
    account_svc: Annotated[AccountSQLService, Depends(get_service(AccountSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
) -> Response:
    logger.info(f"Requisition ref: {requisition_id}")
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    if requisition_id:
        req = await requisition_svc.get_by(
            user_id=user_id, requisition_id=requisition_id
        )
        if req:
            req.accepted = True
            await requisition_svc.update(req)
            account_ids = await client.get_requisition(requisition_id=requisition_id)

            for account_id in account_ids:
                account_data = await client.get_account_detail(account_id)
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
                await account_svc.create(account)
            return Response(status_code=200)
    raise HTTPException(status_code=404, detail="Requisition not found")


@router.get(
    "/{account_id}",
    description="Get the account given the `account_id` for the connected user.",
)
async def get_account(
    account_id: str,
    svc: Annotated[AccountSQLService, Depends(get_service(AccountSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
) -> AccountRead | None:
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    return await svc.get_by(user_id=user_id, account_id=account_id)


@router.get("/", description="List all accounts for the connected user.")
async def get_user_accounts(
    svc: Annotated[AccountSQLService, Depends(get_service(AccountSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
    ordering: OrderingDep,
    paginate: PaginateDep
    # ordering: Annotated[
    #     OrderingFilter,
    #     Query(description="The base ordering to use for results."),
    # ],
    # paginate: Annotated[
    #     bool, Query(description="Whether to paginate response or not.")
    # ] = False,
) -> list[AccountRead] | PaginatedResponse[AccountRead]:
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    return await svc.list_by(ordering=ordering, paginate=paginate, user_id=user_id)


@router.post("/", description="Create a new account for the connected user.")
async def create_account(
    account: AccountCreate,
    svc: Annotated[AccountSQLService, Depends(get_service(AccountSQLService))],
    user_id: Annotated[str, Depends(get_user_id)],
) -> AccountRead:
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    if account.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. The current account must be owned by the current user.",
        )
    else:
        return await svc.create(account)
