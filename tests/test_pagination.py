from http import HTTPStatus

import pytest
import requests

from tests.utils import pages_count


def test_users_pagination_page(app_url, users):
    size = 1
    response = requests.get(f"{app_url}/api/users/?size={size}&page={len(users["items"])}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["total"] == len(users["items"])
    assert response.json()["page"] == len(users["items"])
    assert response.json()["size"] == size
    assert response.json()["pages"] == len(users["items"])
    assert len(response.json()) == 5


def test_users_pagination_size(app_url, users):
    page = 1
    size = 100
    response = requests.get(f"{app_url}/api/users/?size={size}&page={page}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["total"] == len(users["items"])
    assert response.json()["page"] == pages_count(len(users["items"]), size)
    assert response.json()["size"] == size
    assert response.json()["pages"] == pages_count(len(users["items"]), size)
    assert len(response.json()) == 5


@pytest.mark.parametrize("page", [-1, 0, "fafaf"])
def test_invalid_page(app_url, page):
    size = 1
    response = requests.get(f"{app_url}/api/users/?size={size}&page={page}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("size", [-1, 0, "fafaf"])
def test_invalid_size(app_url, size):
    page = 1
    response = requests.get(f"{app_url}/api/users/?size={size}&page={page}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_nonexistent_page(app_url, users):
    size = 1
    response = requests.get(f"{app_url}/api/users/?size={size}&page={len(users["items"]) + 1}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["page"] == len(users["items"]) + 1
    assert response.json()["size"] == size
    assert response.json()["pages"] == response.json()["total"]
    assert response.json()["items"] == []
    assert len(response.json()) == 5


def test_nonexistent_size(app_url):
    page = 1
    size = 999
    response = requests.get(f"{app_url}/api/users/?size={size}&page={page}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_different_results_on_different_pages(app_url, users):
    size = 1
    page = 1
    first_page_response = requests.get(f"{app_url}/api/users/?size={size}&page={page}")
    second_page_response = requests.get(f"{app_url}/api/users/?size={size}&page={page + 1}")
    assert first_page_response.json()["items"] != second_page_response.json()["items"]
