import logging

import dotenv

dotenv.load_dotenv()

import os
import uvicorn

from fastapi_pagination import add_pagination
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers import status, users
from app.database.engine import create_db_and_tables, clean_up_and_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.warning("On startup")
    clean_up_and_tables()
    create_db_and_tables()
    yield
    logging.warning("On shutdown")


app = FastAPI(lifespan=lifespan, debug=True)
app.include_router(status.router)
app.include_router(users.router)
add_pagination(app)

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("APP_URL"), port=int(os.getenv("APP_PORT")))
