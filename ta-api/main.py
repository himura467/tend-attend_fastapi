import os

from dotenv import load_dotenv
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from ta_api.routers import account, admin, auth, event, verify

load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI()

origins = [FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.options("/{rest_of_path}")
async def preflight_handler(rest_of_path: str) -> Response:
    return Response(status_code=status.HTTP_200_OK)


app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
)

app.include_router(
    account.router,
    prefix="/accounts",
    tags=["accounts"],
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    verify.router,
    prefix="/verify",
    tags=["verify"],
)

app.include_router(
    event.router,
    prefix="/events",
    tags=["events"],
)

lambda_handler = Mangum(app)
