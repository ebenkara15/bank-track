import pytest
from requests import HTTPError

from bank_track.infra.bank import GoCardlessClient, GoCardlessTokenManager
from tests.unit.bank.conftest import gocardless_api_mock, gocardless_api_mock_fail

GO_CARDLESS_ENDPOINT = "https://bankaccountdata.gocardless.com/api/v2"


def test_go_cardless_token_manager_object_vars():
    token_mgr = GoCardlessTokenManager("secret_id", "secret_key")

    assert token_mgr.secret_id == "secret_id"
    assert token_mgr.secret_key == "secret_key"
    assert token_mgr.headers == {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    assert token_mgr.token is None


@gocardless_api_mock
def test_go_cardless_token_manager_get_token(token_example):
    token_mgr = GoCardlessTokenManager("secret_id", "secret_key")
    token_mgr.get_token()

    assert token_mgr.token == token_example


def test_go_cardless_token_manager_renew_token():
    token_mgr = GoCardlessTokenManager("secret_id", "secret_key")

    with pytest.raises(NotImplementedError):
        token_mgr._refresh_token()


@gocardless_api_mock
def test_go_cardless_client_object_vars():
    token_mgr = GoCardlessTokenManager("secret_id", "secret_key")
    go_cardless_client = GoCardlessClient(token_mgr)

    assert go_cardless_client.token_manager == token_mgr
    assert go_cardless_client.BASE_ENDPOINT == GO_CARDLESS_ENDPOINT
    assert go_cardless_client.redirect_url == "http://localhost:5173/accounts/verify"
    assert go_cardless_client.headers == {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer access",
    }


@gocardless_api_mock
def test_go_cardless_client_get_institutions_by_country(institutions_list):
    token_mgr = GoCardlessTokenManager("secret_id", "secret_key")
    go_cardless_client = GoCardlessClient(token_mgr)

    institutions = go_cardless_client.get_institutions_by_country("FR")
    assert institutions == institutions_list


@gocardless_api_mock_fail
def test_go_cardless_client_get_institutions_by_country_resp_fail():
    token_mgr = GoCardlessTokenManager("secret_id", "secret_key")
    go_cardless_client = GoCardlessClient(token_mgr)

    with pytest.raises(HTTPError):
        go_cardless_client.get_institutions_by_country("FR")


@gocardless_api_mock
def test_go_cardless_client_get_institutions_by_id(institution_detail):
    token_mgr = GoCardlessTokenManager("secret_id", "secret_key")
    go_cardless_client = GoCardlessClient(token_mgr)

    institution = go_cardless_client.get_institution_by_id("FR0001")
    assert institution == institution_detail


@gocardless_api_mock_fail
def test_go_cardless_client_get_institutions_by_id_resp_fail():
    token_mgr = GoCardlessTokenManager("secret_id", "secret_key")
    go_cardless_client = GoCardlessClient(token_mgr)

    with pytest.raises(HTTPError):
        go_cardless_client.get_institution_by_id("FR0001")
