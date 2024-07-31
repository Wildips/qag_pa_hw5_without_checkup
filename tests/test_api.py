from http import HTTPStatus

import pytest
import requests
from app.models.User import User
from tests.conftest import fill_test_data, users


@pytest.mark.usefixtures("fill_test_data")
def test_users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    user_list = response.json()["items"]
    for user in user_list:
        User.model_validate(user)


@pytest.mark.xfail
@pytest.mark.usefixtures("fill_test_data")
def test_users_no_duplicates(users):
    users_ids = [int(user["id"]) for user in users]
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


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_user_invalid_values(app_url, user_id):
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_user(app_url, user):
    body = {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "avatar": user.avatar}
    response = requests.post(f"{app_url}/api/users/", json=body)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["email"] == user.email
    assert response.json()["first_name"] == user.first_name
    assert response.json()["last_name"] == user.last_name
    assert response.json()["avatar"] == user.avatar
    user_id = int(response.json()["id"])
    assert user_id > 0
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == user.email
    assert response.json()["first_name"] == user.first_name
    assert response.json()["last_name"] == user.last_name
    assert response.json()["avatar"] == user.avatar
    assert response.json()["id"] == user_id


def test_delete_user(app_url, create_user):
    user_id = create_user
    response = requests.delete(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "User deleted"
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "User not found"


def test_update_user(app_url, create_delete_user):
    user_id = create_delete_user["id"]
    user_email = create_delete_user["email"]
    user_first_name = create_delete_user["first_name"]
    user_last_name = create_delete_user["last_name"]
    user_avatar = create_delete_user["avatar"]
    body = {"email": "some@mew.val", "first_name": "some_mew_first_name_val", "last_name": "some_mew_last_name_val",
            "avatar": "http://some_mew_avatar_name_val.html"}
    response = requests.patch(f"{app_url}/api/users/{user_id}", json=body)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] != user_email
    assert response.json()["first_name"] != user_first_name
    assert response.json()["last_name"] != user_last_name
    assert response.json()["avatar"] != user_avatar
    assert response.json()["id"] == user_id


def test_update_user_with_nonexistent_id(app_url, users, user):
    body = {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "avatar": user.avatar}
    response = requests.patch(f"{app_url}/api/users/{len(users["items"]) + 1}", json=body)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_update_user_with_invalid_id(app_url, user_id, user):
    body = {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "avatar": user.avatar}
    response = requests.patch(f"{app_url}/api/users/{user_id}", json=body)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete_user_with_nonexistent_id(app_url, users):
    response = requests.delete(f"{app_url}/api/users/{len(users["items"]) + 1}")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_delete_user_with_invalid_id(app_url, user_id):
    response = requests.delete(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
