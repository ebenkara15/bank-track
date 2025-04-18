from functools import partial, wraps
from typing import Callable

import pytest
from requests_mock import Mocker


GO_CARDLESS_ENDPOINT = "https://bankaccountdata.gocardless.com/api/v2"


@pytest.fixture
def token_example():
    return {
        "access": "access",
        "access_expires": 3600,
        "refresh": "refresh",
        "refresh_expires": 3600,
    }


@pytest.fixture
def institutions_list():
    institutions_list = [
        {
            "id": "FR0001",
            "name": "Banque de France",
            "countries": ["FR", "ES"],
            "bic": "FRLCLYPP",
        },
        {
            "id": "FR0002",
            "name": "Banque de Paris",
            "country": ["FR"],
            "bic": "FBPRKL",
        },
    ]

    return institutions_list


@pytest.fixture
def institution_detail():
    return {
        "id": "FR0001",
        "name": "Banque de France",
        "countries": ["FR", "ES"],
        "bic": "FRLCLYPP",
    }


def gocardless_api_mock(func: Callable, fail_mode: bool = False) -> Mocker:
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Mocker() as m:
            m.post(
                f"{GO_CARDLESS_ENDPOINT}/token/new/",
                json={
                    "access": "access",
                    "access_expires": 3600,
                    "refresh": "refresh",
                    "refresh_expires": 3600,
                },
            )

            if not fail_mode:
                # get_institutions_by_country
                m.get(
                    f"{GO_CARDLESS_ENDPOINT}/institutions/",
                    json=[
                        {
                            "id": "FR0001",
                            "name": "Banque de France",
                            "countries": ["FR", "ES"],
                            "bic": "FRLCLYPP",
                        },
                        {
                            "id": "FR0002",
                            "name": "Banque de Paris",
                            "country": ["FR"],
                            "bic": "FBPRKL",
                        },
                    ],
                )
                # get_institution_by_id
                m.get(
                    f"{GO_CARDLESS_ENDPOINT}/institutions/FR0001",
                    json={
                        "id": "FR0001",
                        "name": "Banque de France",
                        "countries": ["FR", "ES"],
                        "bic": "FRLCLYPP",
                    },
                )
                # create_agreement
                # TODO: Add a response for create_agreement
                m.post(
                    f"{GO_CARDLESS_ENDPOINT}/agreements/enduser/",
                    json={},
                )
                # create_requisition
                # TODO: Add a response for create_requisition
                m.post(
                    f"{GO_CARDLESS_ENDPOINT}/requisitions/",
                    json={},
                )
                # get_requisition
                # TODO: Add a response for get_requisition
                m.get(
                    f"{GO_CARDLESS_ENDPOINT}/requisitions/18a51cd9-8fd7-4709-adbf-63993d0719dd",
                    json={},
                )
                # get_account_detail
                # TODO: Add a response for get_account_detail
                m.get(
                    f"{GO_CARDLESS_ENDPOINT}/accounts/6ed0188b-f318-4ad8-a54f-8c78e18bef52/details",
                    json={},
                )

            else:
                m.get(
                    f"{GO_CARDLESS_ENDPOINT}/institutions/",
                    status_code=400,
                )
                m.get(
                    f"{GO_CARDLESS_ENDPOINT}/institutions/FR0001",
                    status_code=400,
                )

            func(*args, **kwargs)

    return wrapper


gocardless_api_mock_fail: Callable = partial(gocardless_api_mock, fail_mode=True)
