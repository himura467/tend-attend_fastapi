from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from ta_core.features.account import Gender
from ta_core.infrastructure.sqlalchemy.models.sequences.sequence import SequenceUserId
from ta_core.infrastructure.sqlalchemy.repositories.account import UserAccountRepository
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.utils.uuid import generate_uuid


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, hashed_password, birth_date, gender, email, nickname",
    [
        (
            "username",
            "hashed_password",
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            Gender.MALE,
            "test@example.com",
            None,
        ),
    ],
)
async def test_create_user_account_async(
    test_session: AsyncSession,
    username: str,
    hashed_password: str,
    birth_date: datetime,
    gender: Gender,
    email: EmailStr,
    nickname: str | None,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    entity_id = generate_uuid()
    user_id = await SequenceUserId.id_generator(uow)

    user_account = await user_account_repository.create_user_account_async(
        entity_id=entity_id,
        user_id=user_id,
        username=username,
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email=email,
        followee_id=entity_id,
        refresh_token=None,
        nickname=nickname,
    )

    assert user_account is not None
    assert user_account.username == username
    assert user_account.hashed_password == hashed_password
    assert user_account.birth_date == birth_date
    assert user_account.gender == gender
    assert user_account.email == email
    assert user_account.followee_id == entity_id
    assert user_account.refresh_token is None
    assert user_account.nickname == nickname


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, hashed_password, birth_date, gender, email, nickname",
    [
        (
            "username",
            "hashed_password",
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            Gender.MALE,
            "test@example.com",
            None,
        ),
    ],
)
async def test_read_by_username_or_none_async(
    test_session: AsyncSession,
    username: str,
    hashed_password: str,
    birth_date: datetime,
    gender: Gender,
    email: EmailStr,
    nickname: str | None,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    entity_id = generate_uuid()
    user_id = await SequenceUserId.id_generator(uow)

    await user_account_repository.create_user_account_async(
        entity_id=entity_id,
        user_id=user_id,
        username=username,
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email=email,
        followee_id=entity_id,
        refresh_token=None,
        nickname=nickname,
    )
    user_account = await user_account_repository.read_by_username_or_none_async(
        username=username
    )

    assert user_account is not None
    assert user_account.username == username
    assert user_account.hashed_password == hashed_password
    assert user_account.birth_date == birth_date.replace(tzinfo=None)
    assert user_account.gender == gender
    assert user_account.email == email
    assert user_account.followee_id == entity_id
    assert user_account.refresh_token is None
    assert user_account.nickname == nickname


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, hashed_password, birth_date, gender, email, nickname",
    [
        (
            "username",
            "hashed_password",
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            Gender.MALE,
            "test@example.com",
            None,
        ),
    ],
)
async def test_read_by_email_or_none_async(
    test_session: AsyncSession,
    username: str,
    hashed_password: str,
    birth_date: datetime,
    gender: Gender,
    email: EmailStr,
    nickname: str | None,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    entity_id = generate_uuid()
    user_id = await SequenceUserId.id_generator(uow)

    await user_account_repository.create_user_account_async(
        entity_id=entity_id,
        user_id=user_id,
        username=username,
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email=email,
        followee_id=entity_id,
        refresh_token=None,
        nickname=nickname,
    )
    user_account = await user_account_repository.read_by_email_or_none_async(
        email=email
    )

    assert user_account is not None
    assert user_account.username == username
    assert user_account.hashed_password == hashed_password
    assert user_account.birth_date == birth_date.replace(tzinfo=None)
    assert user_account.gender == gender
    assert user_account.email == email
    assert user_account.followee_id == entity_id
    assert user_account.refresh_token is None
    assert user_account.nickname == nickname


@pytest.mark.asyncio
async def test_read_with_followers_by_id_or_none_async(
    test_session: AsyncSession,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    user0_entity_id = generate_uuid()
    user1_entity_id = generate_uuid()
    user0_user_id = await SequenceUserId.id_generator(uow)
    user1_user_id = await SequenceUserId.id_generator(uow)

    hashed_password = "hashed_password"
    birth_date = datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
    gender = Gender.MALE
    nickname = None

    await user_account_repository.create_user_account_async(
        entity_id=user0_entity_id,
        user_id=user0_user_id,
        username="username0",
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email="user0@example.com",
        followee_id=user0_entity_id,
        refresh_token=None,
        nickname=nickname,
    )
    await user_account_repository.create_user_account_async(
        entity_id=user1_entity_id,
        user_id=user1_user_id,
        username="username1",
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email="user1@example.com",
        followee_id=user0_entity_id,
        refresh_token=None,
        nickname=nickname,
    )

    followee = await user_account_repository.read_with_followers_by_id_or_none_async(
        record_id=user0_entity_id
    )
    follower = await user_account_repository.read_with_followers_by_id_or_none_async(
        record_id=user1_entity_id
    )

    assert followee is not None
    assert follower is not None
    assert len(followee.followers) == 2
    assert followee.followers[0].id == user0_entity_id
    assert followee.followers[1].id == user1_entity_id
