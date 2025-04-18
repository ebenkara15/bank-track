from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bank_track.api.database import get_db
from bank_track.api.routers.account import router as account_router
from bank_track.api.routers.balance import router as balance_router
from bank_track.api.routers.categories import router as categories_router
from bank_track.api.routers.transaction import router as transaction_router
from bank_track.api.routers.webhook import router as webhooks_router
from bank_track.core.models.sql import BaseSQLModel


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db = get_db()
        db.init_schema(BaseSQLModel.metadata)
        yield

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ##################
    # Account router #
    ##################
    app.include_router(account_router)

    ##################
    # Balance router #
    ##################
    app.include_router(balance_router)

    ######################
    # Transaction router #
    ######################
    app.include_router(transaction_router)

    ###########################
    # Expense category router #
    ###########################
    app.include_router(categories_router)

    ########################
    # User webhooks router #
    ########################
    app.include_router(webhooks_router)

    @app.get("/healthz", tags=["probes"])
    @app.get("/health", tags=["probes"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="main:app", reload=True, host="localhost", port=8000, log_level="info"
    )
