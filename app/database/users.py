from http import HTTPStatus
from typing import Type

from fastapi import APIRouter, HTTPException
from fastapi_pagination import paginate, Page
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlmodel import Session, select

from app.database import users
from app.models.User import User, UserCreate, UserUpdate
from app.database.engine import engine

disable_installed_extensions_check()

router = APIRouter(prefix="/api/users")


# @router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> Type[User]:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    with Session(engine) as session:
        user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


# @router.get("/", status_code=HTTPStatus.OK, response_model=Page[User])
# async def get_users() -> Page[User]:
def get_users() -> Page[User]:
    with Session(engine) as session:
        statement = select(User)
        return paginate(session.exec(statement).all())


# @router.post("/", status_code=HTTPStatus.CREATED)
# async def create_user(user: User) -> User:
def create_user(user: User) -> User:
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


# @router.patch("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_id: int, user: User) -> Type[User]:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = user.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


# @router.delete("/{user_id}", status_code=HTTPStatus.OK)
def delete_user(user_id: int):
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
        session.delete(user)
        session.commit()
    return {"message": "User deleted"}
