import json
import os
from http import HTTPStatus
from pathlib import Path

import dotenv
import pytest
import requests
import faker

from app.models.User import User

fake = faker.Faker()


@pytest.fixture(scope="session", autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope="session")
def app_url():
    return f"http://{os.getenv("APP_URL")}:{os.getenv("APP_PORT")}"


@pytest.fixture(scope="session")
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
def random_user_data() -> User:
    user = User(email=fake.ascii_free_email(), first_name=fake.first_name_female(), last_name=fake.last_name_female(),
                avatar=fake.uri())
    return user


@pytest.fixture()
def random_test_user(random_user_data: User, app_url) -> User:
    response = requests.post(f"{app_url}/api/users/", json=random_user_data.model_dump())
    assert response.status_code == HTTPStatus.CREATED
    yield User(**response.json())


@pytest.fixture()
def create_delete_user(random_user_data: User, app_url) -> User:
    response = requests.post(f"{app_url}/api/users/", json=random_user_data.model_dump())
    assert response.status_code == HTTPStatus.CREATED
    random_user_data = User(**response.json())
    yield random_user_data
    response = requests.delete(f"{app_url}/api/users/{response.json()["id"]}")
    assert response.status_code == HTTPStatus.OK
