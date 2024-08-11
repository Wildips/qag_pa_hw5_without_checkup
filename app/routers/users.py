from http import HTTPStatus
from typing import Type, Any, Coroutine

from fastapi import APIRouter, HTTPException
from fastapi_pagination import paginate, Page
from fastapi_pagination.utils import disable_installed_extensions_check

from app.database import users
from app.models.User import User, UserCreate, UserUpdate

disable_installed_extensions_check()

router = APIRouter(prefix="/api/users")


@router.get("/{user_id}", status_code=HTTPStatus.OK)
# def get_user(user_id: int) -> Coroutine[Any, Any, Type[User]]:
def get_user(user_id: int) -> Coroutine[Any, Any, Type[User]]:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    user = users.get_user(user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


@router.get("/", status_code=HTTPStatus.OK, response_model=None)#response_model=Page[User])
# async def get_users() -> Page[User]:
# def get_users() -> Page[User]:
def get_users() -> Coroutine[Any, Any, Type[User]]:
    # return await paginate(users.get_users())
    return paginate(users.get_users())


@router.post("/", status_code=HTTPStatus.CREATED, response_model=None)
# async def create_user(user: User) -> Type[User]:
# async def create_user(user: User) -> Coroutine[Any, Any, User]:
def create_user(user: User) -> Coroutine[Any, Any, User]:
    UserCreate.model_validate(user.model_dump())
    # return await users.create_user(user)
    return users.create_user(user)


@router.patch("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_id: int, user: User) -> Type[User]:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    UserUpdate.model_validate(user.model_dump())
    return users.update_user(user_id, user)


@router.delete("/{user_id}", status_code=HTTPStatus.OK)
def delete_user(user_id: int):
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    user = users.get_user(user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    users.delete_user(user_id)
    return {"message": "User deleted"}
