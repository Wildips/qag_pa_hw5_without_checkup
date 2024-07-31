from http import HTTPStatus

import requests


def test_app_status(app_url):
    response = requests.get(f"{app_url}/status/")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["database"], "Init data are absent"
