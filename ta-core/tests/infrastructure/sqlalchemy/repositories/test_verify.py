from datetime import datetime

import pytest
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from ta_core.infrastructure.sqlalchemy.repositories.account import HostAccountRepository
from ta_core.infrastructure.sqlalchemy.repositories.verify import (
    HostVerificationRepository,
)
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.utils.uuid import generate_uuid


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host_name, hashed_password, host_email, verification_token, token_expires_at",
    [
        (
            "host_name",
            "hashed_password",
            "test@example.com",
            "verification_token",
            datetime(2000, 1, 2, 3, 4, 5),
        ),
    ],
)
async def test_create_host_verification_async(
    test_session: AsyncSession,
    host_name: str,
    hashed_password: str,
    host_email: EmailStr,
    verification_token: str,
    token_expires_at: datetime,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    host_account_repository = HostAccountRepository(uow)
    host_verification_repository = HostVerificationRepository(uow)

    await host_account_repository.create_host_account_async(
        entity_id=generate_uuid(),
        host_name=host_name,
        hashed_password=hashed_password,
        email=host_email,
    )
    host_verification = (
        await host_verification_repository.create_host_verification_async(
            entity_id=generate_uuid(),
            host_email=host_email,
            verification_token=verification_token,
            token_expires_at=token_expires_at,
        )
    )

    assert host_verification is not None
    assert host_verification.host_email == host_email
    assert host_verification.verification_token == verification_token
    assert host_verification.token_expires_at == token_expires_at


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host_name, hashed_password, host_email, verification_token, token_expires_at",
    [
        (
            "host_name",
            "hashed_password",
            "test@example.com",
            "verification_token",
            datetime(2000, 1, 2, 3, 4, 5),
        ),
    ],
)
async def test_read_latest_by_host_email_or_none_async(
    test_session: AsyncSession,
    host_name: str,
    hashed_password: str,
    host_email: EmailStr,
    verification_token: str,
    token_expires_at: datetime,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    host_account_repository = HostAccountRepository(uow)
    host_verification_repository = HostVerificationRepository(uow)

    await host_account_repository.create_host_account_async(
        entity_id=generate_uuid(),
        host_name=host_name,
        hashed_password=hashed_password,
        email=host_email,
    )
    await host_verification_repository.create_host_verification_async(
        entity_id=generate_uuid(),
        host_email=host_email,
        verification_token=verification_token,
        token_expires_at=token_expires_at,
    )
    host_verification = (
        await host_verification_repository.read_latest_by_host_email_or_none_async(
            host_email=host_email
        )
    )

    assert host_verification is not None
    assert host_verification.host_email == host_email
    assert host_verification.verification_token == verification_token
    assert host_verification.token_expires_at == token_expires_at
