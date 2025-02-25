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
        followee_ids=set(),
        follower_ids=set(),
        refresh_token=None,
        nickname=nickname,
    )

    assert user_account is not None
    assert user_account.username == username
    assert user_account.hashed_password == hashed_password
    assert user_account.birth_date == birth_date
    assert user_account.gender == gender
    assert user_account.email == email
    assert user_account.followees == []
    assert user_account.followers == []
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
        followee_ids=set(),
        follower_ids=set(),
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
    assert user_account.followees == []
    assert user_account.followers == []
    assert user_account.refresh_token is None
    assert user_account.nickname == nickname


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "usernames, hashed_password, birth_date, gender, emails, nickname",
    [
        (
            ["username0", "username1"],
            "hashed_password",
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            Gender.MALE,
            ["user0@example.com", "user1@example.com"],
            None,
        ),
    ],
)
async def test_read_by_usernames_async(
    test_session: AsyncSession,
    usernames: list[str],
    hashed_password: str,
    birth_date: datetime,
    gender: Gender,
    emails: list[EmailStr],
    nickname: str | None,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    for username, email in zip(usernames, emails):
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
            followee_ids=set(),
            follower_ids=set(),
            refresh_token=None,
            nickname=nickname,
        )

    user_accounts = await user_account_repository.read_by_usernames_async(
        usernames=set(usernames)
    )

    assert len(user_accounts) == len(usernames)
    for user_account, username, email in zip(user_accounts, usernames, emails):
        assert user_account is not None
        assert user_account.username == username
        assert user_account.hashed_password == hashed_password
        assert user_account.birth_date == birth_date.replace(tzinfo=None)
        assert user_account.gender == gender
        assert user_account.email == email
        assert user_account.followees == []
        assert user_account.followers == []
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
        followee_ids=set(),
        follower_ids=set(),
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
    assert user_account.followees == []
    assert user_account.followers == []
    assert user_account.refresh_token is None
    assert user_account.nickname == nickname


@pytest.mark.asyncio
async def test_read_with_followees_by_id_or_none_async(
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
        followee_ids=set(),
        follower_ids=set(),
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
        followee_ids={user0_entity_id},
        follower_ids=set(),
        refresh_token=None,
        nickname=nickname,
    )

    user1 = await user_account_repository.read_with_followees_by_id_or_none_async(
        record_id=user1_entity_id
    )

    assert user1 is not None
    assert len(user1.followees) == 1
    assert len(user1.followers) == 0
    assert user1.followees[0].id == user0_entity_id
    assert user1.followees[0].user_id == user0_user_id
    assert user1.followees[0].followees == []
    assert user1.followees[0].followers == []

    user0 = await user_account_repository.read_with_followers_by_id_or_none_async(
        record_id=user0_entity_id
    )

    assert user0 is not None
    assert len(user0.followees) == 0
    assert len(user0.followers) == 1
    assert user0.followers[0].id == user1_entity_id
    assert user0.followers[0].user_id == user1_user_id
    assert user0.followers[0].followees == []
    assert user0.followers[0].followers == []


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
        followee_ids=set(),
        follower_ids=set(),
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
        followee_ids=set(),
        follower_ids={user0_entity_id},
        refresh_token=None,
        nickname=nickname,
    )

    user1 = await user_account_repository.read_with_followers_by_id_or_none_async(
        record_id=user1_entity_id
    )

    assert user1 is not None
    assert len(user1.followees) == 0
    assert len(user1.followers) == 1
    assert user1.followers[0].id == user0_entity_id
    assert user1.followers[0].user_id == user0_user_id
    assert user1.followers[0].followees == []
    assert user1.followers[0].followers == []

    user0 = await user_account_repository.read_with_followees_by_id_or_none_async(
        record_id=user0_entity_id
    )

    assert user0 is not None
    assert len(user0.followees) == 1
    assert len(user0.followers) == 0
    assert user0.followees[0].id == user1_entity_id
    assert user0.followees[0].user_id == user1_user_id
    assert user0.followees[0].followees == []
    assert user0.followees[0].followers == []
