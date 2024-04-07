from fastapi import FastAPI

from ta_api.routers import auth

app = FastAPI()

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)
