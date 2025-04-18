from fastapi.testclient import TestClient
from loguru import logger

from bank_track.api.main import create_app
from bank_track.api.security import get_user_id


def override_get_user_id():
    return "user_2be"


app = create_app()
app.dependency_overrides[get_user_id] = override_get_user_id
client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthz() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unauth_get_transactions() -> None:
    response = client.get("/transactions/")
    logger.info(response.json())

    assert response.status_code == 200


def test_unauth_get_transaction() -> None:
    response = client.get("/transactions/0061109c-4b09-4a1c-8a0e-61d6bcbe20c8")

    assert response.status_code == 404
    assert response.json() == {"detail": "No resource found."}
