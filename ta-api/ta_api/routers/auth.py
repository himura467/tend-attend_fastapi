from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from ta_core.dtos.auth import (
    CreateAccountRequest,
    CreateAccountResponse,
    LoginForAuthTokenResponse,
    RefreshAuthTokenRequest,
    RefreshAuthTokenResponse,
)
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.models.commons.auth import Account
from ta_core.infrastructure.sqlalchemy.repositories.auth import AuthRepository
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.auth import AuthUseCase

router = APIRouter()


@router.post("/account", name="Create Account", response_model=CreateAccountResponse)
async def create_account(
    request: CreateAccountRequest, session: AsyncSession = Depends(get_db_async)
) -> CreateAccountResponse:
    login_id = request.login_id
    login_password = request.login_password
    group = request.group

    auth_repository = AuthRepository(
        session=session,
        model=Account,
    )
    unit_of_work = SqlalchemyUnitOfWork(session=session)
    use_case = AuthUseCase(
        auth_repository=auth_repository,
        unit_of_work=unit_of_work,
    )

    return await use_case.create_account_async(
        login_id=login_id, login_password=login_password, group=group
    )


@router.post(
    "/token", name="Create Auth Token", response_model=LoginForAuthTokenResponse
)
async def login_for_auth_token(
    res: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_async),
) -> LoginForAuthTokenResponse:
    login_id = form_data.username
    login_password = form_data.password

    auth_repository = AuthRepository(
        session=session,
        model=Account,
    )
    unit_of_work = SqlalchemyUnitOfWork(session=session)
    use_case = AuthUseCase(
        auth_repository=auth_repository,
        unit_of_work=unit_of_work,
    )

    response = await use_case.authenticate_async(
        login_id=login_id, login_password=login_password
    )
    if response.auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    res.set_cookie(
        key="access_token",
        value=response.auth_token.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=response.access_token_max_age,
    )
    res.set_cookie(
        key="refresh_token",
        value=response.auth_token.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=response.refresh_token_max_age,
    )

    return LoginForAuthTokenResponse(error_codes=response.error_codes)


@router.post(
    "/refresh", name="Refresh Auth Token", response_model=RefreshAuthTokenResponse
)
async def refresh_auth_token(
    request: RefreshAuthTokenRequest,
    res: Response,
    session: AsyncSession = Depends(get_db_async),
) -> RefreshAuthTokenResponse:
    refresh_token = request.refresh_token

    auth_repository = AuthRepository(
        session=session,
        model=Account,
    )
    unit_of_work = SqlalchemyUnitOfWork(session=session)
    use_case = AuthUseCase(
        auth_repository=auth_repository,
        unit_of_work=unit_of_work,
    )

    response = await use_case.refresh_auth_token_async(refresh_token=refresh_token)
    if response.auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    res.set_cookie(
        key="access_token",
        value=response.auth_token.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=response.access_token_max_age,
    )
    res.set_cookie(
        key="refresh_token",
        value=response.auth_token.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=response.refresh_token_max_age,
    )

    return RefreshAuthTokenResponse(error_codes=response.error_codes)
