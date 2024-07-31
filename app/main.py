import logging
import os
from contextlib import asynccontextmanager

import dotenv
from fastapi_pagination import add_pagination

dotenv.load_dotenv()

import uvicorn
from fastapi import FastAPI

from app.routers import status, users
from app.database.engine import create_db_and_tables, clean_up_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.warning("On startup")
    create_db_and_tables()
    yield
    # clean_up_and_tables()
    logging.warning("On shutdown")


app = FastAPI(lifespan=lifespan, debug=True)
app.include_router(status.router)
app.include_router(users.router)
add_pagination(app)

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("APP_URL"), port=int(os.getenv("APP_PORT")))
