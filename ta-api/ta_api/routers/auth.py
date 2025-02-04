from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio.session import AsyncSession
from ta_core.dtos.auth import (
    AuthToken,
    RefreshAuthTokenRequest,
    RefreshAuthTokenResponse,
)
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.auth import AuthUseCase

from ta_api.constants import ACCESS_TOKEN_NAME, COOKIE_DOMAIN, REFRESH_TOKEN_NAME

router = APIRouter()


@router.post(path="/token", name="Create Auth Token", response_model=AuthToken)
async def create_auth_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_async),
) -> AuthToken:
    auth_info_json = form_data.username
    password = form_data.password

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = AuthUseCase(uow=uow)

    res = await use_case.authenticate_async(
        auth_info_json=auth_info_json, password=password
    )
    if res.auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect auth_info or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    response.set_cookie(
        key=ACCESS_TOKEN_NAME,
        value=res.auth_token.access_token,
        max_age=res.access_token_max_age,
        expires=datetime.now(timezone.utc)
        + timedelta(seconds=res.access_token_max_age),
        path="/",
        domain=COOKIE_DOMAIN,
        secure=True,
        httponly=True,
        samesite="strict",
    )
    response.set_cookie(
        key=REFRESH_TOKEN_NAME,
        value=res.auth_token.refresh_token,
        max_age=res.refresh_token_max_age,
        expires=datetime.now(timezone.utc)
        + timedelta(seconds=res.refresh_token_max_age),
        path="/",
        domain=COOKIE_DOMAIN,
        secure=True,
        httponly=True,
        samesite="strict",
    )

    return res.auth_token


@router.post(
    path="/token/refresh",
    name="Refresh Auth Token",
    response_model=RefreshAuthTokenResponse,
)
async def refresh_auth_token(
    req: RefreshAuthTokenRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_async),
) -> RefreshAuthTokenResponse:
    refresh_token = req.refresh_token

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = AuthUseCase(uow=uow)

    res = await use_case.refresh_auth_token_async(refresh_token=refresh_token)
    if res.auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    response.set_cookie(
        key=ACCESS_TOKEN_NAME,
        value=res.auth_token.access_token,
        max_age=res.access_token_max_age,
        expires=datetime.now(timezone.utc)
        + timedelta(seconds=res.access_token_max_age),
        path="/",
        domain=COOKIE_DOMAIN,
        secure=True,
        httponly=True,
        samesite="strict",
    )
    response.set_cookie(
        key=REFRESH_TOKEN_NAME,
        value=res.auth_token.refresh_token,
        max_age=res.refresh_token_max_age,
        expires=datetime.now(timezone.utc)
        + timedelta(seconds=res.refresh_token_max_age),
        path="/",
        domain=COOKIE_DOMAIN,
        secure=True,
        httponly=True,
        samesite="strict",
    )

    return RefreshAuthTokenResponse(error_codes=res.error_codes)
