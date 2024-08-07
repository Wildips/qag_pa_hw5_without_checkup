from http import HTTPStatus

import requests


def test_app_status(app_url):
    response = requests.get(f"{app_url}/status/")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["database"], "Init data are absent"


def test_service_response_time(app_url):
    response = requests.get(app_url)
    assert response.elapsed.total_seconds() < 1


def test_service_headers(app_url):
    response = requests.get(app_url)
    assert 'Content-Type' in response.headers
    assert response.headers['Content-Type'] == 'application/json'
