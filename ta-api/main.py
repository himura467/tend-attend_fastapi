from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ta_api.routers import account, auth, verify, event

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
