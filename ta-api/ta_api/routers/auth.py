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
        key="access_token",
        value=res.auth_token.access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=res.access_token_max_age,
    )
    response.set_cookie(
        key="refresh_token",
        value=res.auth_token.refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=res.refresh_token_max_age,
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
        key="access_token",
        value=res.auth_token.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=res.access_token_max_age,
    )
    response.set_cookie(
        key="refresh_token",
        value=res.auth_token.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=res.refresh_token_max_age,
    )

    return RefreshAuthTokenResponse(error_codes=res.error_codes)
