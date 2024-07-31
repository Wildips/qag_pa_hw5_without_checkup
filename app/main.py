import os

import dotenv
from fastapi_pagination import add_pagination

dotenv.load_dotenv()

import uvicorn
from fastapi import FastAPI

from routers import status, users
from app.database.engine import create_db_and_tables, clean_up_and_tables

app = FastAPI(debug=True)
app.include_router(status.router)
app.include_router(users.router)
add_pagination(app)

if __name__ == "__main__":
    clean_up_and_tables()
    create_db_and_tables()
    uvicorn.run(app, host=os.getenv("APP_URL"), port=int(os.getenv("APP_PORT")))
