from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from ta_core.features.account import Gender
from ta_core.infrastructure.sqlalchemy.models.sequences.sequence import SequenceUserId
from ta_core.infrastructure.sqlalchemy.repositories.account import UserAccountRepository
from ta_core.infrastructure.sqlalchemy.repositories.verify import (
    EmailVerificationRepository,
)
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.utils.uuid import UUID, generate_uuid


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, hashed_password, birth_date, gender, email, nickname, verification_token, token_expires_at",
    [
        (
            "username",
            "hashed_password",
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            Gender.MALE,
            "test@example.com",
            None,
            generate_uuid(),
            datetime(2000, 1, 2, 3, 4, 5, tzinfo=ZoneInfo("UTC")),
        ),
    ],
)
async def test_create_email_verification_async(
    test_session: AsyncSession,
    username: str,
    hashed_password: str,
    birth_date: datetime,
    gender: Gender,
    email: EmailStr,
    nickname: str | None,
    verification_token: UUID,
    token_expires_at: datetime,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)
    email_verification_repository = EmailVerificationRepository(uow)

    entity_id = generate_uuid()
    user_id = await SequenceUserId.id_generator(uow)

    await user_account_repository.create_user_account_async(
        entity_id=generate_uuid(),
        user_id=user_id,
        username=username,
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email=email,
        followee_ids=set(),
        follower_ids=set(),
        refresh_token=None,
        nickname=nickname,
    )
    email_verification = (
        await email_verification_repository.create_email_verification_async(
            entity_id=entity_id,
            email=email,
            verification_token=verification_token,
            token_expires_at=token_expires_at,
        )
    )

    assert email_verification is not None
    assert email_verification.id == entity_id
    assert email_verification.email == email
    assert email_verification.verification_token == verification_token
    assert email_verification.token_expires_at == token_expires_at

    non_existent_email_verification = (
        await email_verification_repository.create_email_verification_async(
            entity_id=generate_uuid(),
            email="non_existent" + email,
            verification_token=verification_token,
            token_expires_at=token_expires_at,
        )
    )

    assert non_existent_email_verification is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, hashed_password, birth_date, gender, email, nickname, verification_token, token_expires_at",
    [
        (
            "username",
            "hashed_password",
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            Gender.MALE,
            "test@example.com",
            None,
            generate_uuid(),
            datetime(2000, 1, 2, 3, 4, 5, tzinfo=ZoneInfo("UTC")),
        ),
    ],
)
async def test_read_latest_by_email_or_none_async(
    test_session: AsyncSession,
    username: str,
    hashed_password: str,
    birth_date: datetime,
    gender: Gender,
    email: EmailStr,
    nickname: str | None,
    verification_token: UUID,
    token_expires_at: datetime,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)
    email_verification_repository = EmailVerificationRepository(uow)

    entity_id = generate_uuid()
    user_id = await SequenceUserId.id_generator(uow)

    await user_account_repository.create_user_account_async(
        entity_id=generate_uuid(),
        user_id=user_id,
        username=username,
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email=email,
        followee_ids=set(),
        follower_ids=set(),
        refresh_token=None,
        nickname=nickname,
    )
    await email_verification_repository.create_email_verification_async(
        entity_id=entity_id,
        email=email,
        verification_token=verification_token,
        token_expires_at=token_expires_at,
    )
    email_verification = (
        await email_verification_repository.read_latest_by_email_or_none_async(
            email=email
        )
    )

    assert email_verification is not None
    assert email_verification.id == entity_id
    assert email_verification.email == email
    assert email_verification.verification_token == verification_token
    assert email_verification.token_expires_at == token_expires_at.replace(tzinfo=None)

    non_existent_email_verification = (
        await email_verification_repository.read_latest_by_email_or_none_async(
            email="non_existent" + email
        )
    )

    assert non_existent_email_verification is None
