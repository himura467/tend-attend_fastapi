import os
from typing import Awaitable, Callable

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, status
from mangum import Mangum
from starlette.middleware.base import BaseHTTPMiddleware

from ta_api.routers import account, admin, auth, event, verify

load_dotenv()
FRONTEND_URLS = os.getenv("FRONTEND_URLS")
ALLOWED_ORIGINS = FRONTEND_URLS.split(",")

app = FastAPI()


class CORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response: Response
        if request.method == "OPTIONS":
            response = Response(status_code=status.HTTP_200_OK)
        else:
            response = await call_next(request)

        origin = request.headers.get("origin")
        if origin in ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*, x-api-key"

        return response


app.add_middleware(CORSMiddleware)

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
