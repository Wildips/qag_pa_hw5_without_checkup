from http import HTTPStatus

import faker
import pytest
import requests
from app.models.User import User
from tests.conftest import fill_test_data, users

fake = faker.Faker()


@pytest.mark.usefixtures("fill_test_data")
def test_users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    user_list = response.json()["items"]
    for user in user_list:
        User.model_validate(user)


@pytest.mark.usefixtures("fill_test_data")
def test_users_no_duplicates(users):
    users_ids = [int(user["id"]) for user in users["items"]]
    assert len(users_ids) == len(set(users_ids))


def test_user(app_url, fill_test_data):
    for user_id in (fill_test_data[0], fill_test_data[-1]):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK
        user = response.json()
        User.model_validate(user)


def test_user_nonexistent_values(app_url, users):
    response = requests.get(f"{app_url}/api/users/{len(users["items"]) + 1}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "User not found"


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_user_invalid_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_user(app_url, random_user_data: User):
    response = requests.post(f"{app_url}/api/users/", json=random_user_data.model_dump())
    assert response.status_code == HTTPStatus.CREATED
    created_user = User(**response.json())
    assert random_user_data.email == created_user.email
    assert random_user_data.first_name == created_user.first_name
    assert random_user_data.last_name == created_user.last_name
    assert random_user_data.avatar == created_user.avatar
    assert created_user.id
    response = requests.get(f"{app_url}/api/users/{created_user.id}")
    assert response.status_code == HTTPStatus.OK
    checking_user = User(**response.json())
    assert created_user == checking_user


def test_delete_user(app_url, random_test_user: User):
    response = requests.delete(f"{app_url}/api/users/{random_test_user.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "User deleted"
    response = requests.get(f"{app_url}/api/users/{random_test_user.id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "User not found"


def test_update_user(app_url, create_delete_user: User):
    body = {"email": fake.ascii_free_email(), "first_name": fake.first_name_female(),
            "last_name": fake.last_name_female(), "avatar": fake.uri()}
    response = requests.patch(f"{app_url}/api/users/{create_delete_user.id}", json=body)
    updated_user_data = User(**response.json())
    assert response.status_code == HTTPStatus.OK
    assert updated_user_data.email != create_delete_user.email
    assert updated_user_data.first_name != create_delete_user.first_name
    assert updated_user_data.last_name != create_delete_user.last_name
    assert updated_user_data.avatar != create_delete_user.avatar
    assert updated_user_data.id == create_delete_user.id


def test_update_user_with_nonexistent_id(app_url, users, random_user_data: User):
    response = requests.patch(f"{app_url}/api/users/{len(users["items"]) + 1}", json=random_user_data.model_dump())
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "User not found"


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_update_user_with_invalid_id(app_url, user_id, random_user_data: User):
    response = requests.patch(f"{app_url}/api/users/{user_id}", json=random_user_data.model_dump())
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete_user_with_nonexistent_id(app_url, users):
    response = requests.delete(f"{app_url}/api/users/{len(users["items"]) + 1}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "User not found"


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_delete_user_with_invalid_id(app_url, user_id):
    response = requests.delete(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
