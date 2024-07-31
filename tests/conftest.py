import json
import os
from http import HTTPStatus
from pathlib import Path

import dotenv
import pytest
import requests

from faker import Faker

from app.models.User import User

fake = Faker()


@pytest.fixture(scope="session", autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope="session")
def app_url():
    return f"http://{os.getenv("APP_URL")}:{os.getenv("APP_PORT")}"


@pytest.fixture(scope="module")
def fill_test_data(app_url):
    with open(Path(__file__).parent.parent.joinpath("users.json").absolute()) as f:
        test_data_users = json.load(f)
    api_users = []
    for user in test_data_users:
        response = requests.post(f"{app_url}/api/users/", json=user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")


@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()


@pytest.fixture()
def user():
    return User(email=fake.ascii_free_email(), first_name=fake.first_name_female(), last_name=fake.last_name_female(),
                avatar=fake.uri())


@pytest.fixture()
def create_user(user, app_url):
    body = {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "avatar": user.avatar}
    response = requests.post(f"{app_url}/api/users/", json=body)
    assert response.status_code == HTTPStatus.CREATED
    yield response.json()["id"]


@pytest.fixture()
def create_delete_user(user, app_url):
    body = {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "avatar": user.avatar}
    response = requests.post(f"{app_url}/api/users/", json=body)
    assert response.status_code == HTTPStatus.CREATED
    yield response.json()
    response = requests.delete(f"{app_url}/api/users/{response.json()["id"]}")
    assert response.status_code == HTTPStatus.OK
