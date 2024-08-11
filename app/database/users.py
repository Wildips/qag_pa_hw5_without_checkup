from http import HTTPStatus
from typing import Type

from fastapi import APIRouter, HTTPException
from fastapi_pagination import paginate, Page
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlmodel import Session, select

from app.models.User import User
from app.database.engine import engine

disable_installed_extensions_check()

router = APIRouter(prefix="/api/users")


def get_user(user_id: int) -> Type[User]:
    with Session(engine) as session:
        user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


def get_users() -> Page[list[User]]:
    with Session(engine) as session:
        statement = select(User)
        return paginate(session.exec(statement).all())


def create_user(user: User) -> User:
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def update_user(user_id: int, user: User) -> Type[User]:
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


def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
        session.delete(user)
        session.commit()
    return {"message": "User deleted"}
