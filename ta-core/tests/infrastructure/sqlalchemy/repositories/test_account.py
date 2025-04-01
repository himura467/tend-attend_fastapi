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
    assert user_account.id == entity_id
    assert user_account.user_id == user_id
    assert user_account.username == username
    assert user_account.hashed_password == hashed_password
    assert user_account.refresh_token is None
    assert user_account.nickname == nickname
    assert user_account.birth_date == birth_date
    assert user_account.gender == gender
    assert user_account.email == email
    assert user_account.email_verified is False
    assert user_account.followee_ids == []
    assert user_account.followees == []
    assert user_account.follower_ids == []
    assert user_account.followers == []

    user_id_duplicated_entity_id = generate_uuid()

    user_id_duplicated_user_account = (
        await user_account_repository.create_user_account_async(
            entity_id=user_id_duplicated_entity_id,
            user_id=user_id,
            username="user_id_duplicated" + username,
            hashed_password=hashed_password,
            birth_date=birth_date,
            gender=gender,
            email="user_id_duplicated" + email,
            followee_ids=set(),
            follower_ids=set(),
            refresh_token=None,
            nickname=nickname,
        )
    )

    assert user_id_duplicated_user_account is None

    username_duplicated_entity_id = generate_uuid()
    username_duplicated_user_id = await SequenceUserId.id_generator(uow)

    username_duplicated_user_account = (
        await user_account_repository.create_user_account_async(
            entity_id=username_duplicated_entity_id,
            user_id=username_duplicated_user_id,
            username=username,
            hashed_password=hashed_password,
            birth_date=birth_date,
            gender=gender,
            email="username_duplicated" + email,
            followee_ids=set(),
            follower_ids=set(),
            refresh_token=None,
            nickname=nickname,
        )
    )

    assert username_duplicated_user_account is None

    email_duplicated_entity_id = generate_uuid()
    email_duplicated_user_id = await SequenceUserId.id_generator(uow)

    email_duplicated_user_account = (
        await user_account_repository.create_user_account_async(
            entity_id=email_duplicated_entity_id,
            user_id=email_duplicated_user_id,
            username="email_duplicated" + username,
            hashed_password=hashed_password,
            birth_date=birth_date,
            gender=gender,
            email=email,
            followee_ids=set(),
            follower_ids=set(),
            refresh_token=None,
            nickname=nickname,
        )
    )

    assert email_duplicated_user_account is None


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
    assert user_account.id == entity_id
    assert user_account.user_id == user_id
    assert user_account.username == username
    assert user_account.hashed_password == hashed_password
    assert user_account.refresh_token is None
    assert user_account.nickname == nickname
    assert user_account.birth_date == birth_date.replace(tzinfo=None)
    assert user_account.gender == gender
    assert user_account.email == email
    assert user_account.email_verified is False
    assert user_account.followee_ids == []
    assert user_account.followees == []
    assert user_account.follower_ids == []
    assert user_account.followers == []


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

    entity_ids = [generate_uuid() for _ in range(len(usernames))]
    user_ids = [await SequenceUserId.id_generator(uow) for _ in range(len(usernames))]

    for username, email, entity_id, user_id in zip(
        usernames, emails, entity_ids, user_ids
    ):
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
    for user_account, username, email, entity_id, user_id in zip(
        user_accounts, usernames, emails, entity_ids, user_ids
    ):
        assert user_account is not None
        assert user_account.id == entity_id
        assert user_account.user_id == user_id
        assert user_account.username == username
        assert user_account.hashed_password == hashed_password
        assert user_account.refresh_token is None
        assert user_account.nickname == nickname
        assert user_account.birth_date == birth_date.replace(tzinfo=None)
        assert user_account.gender == gender
        assert user_account.email == email
        assert user_account.email_verified is False
        assert user_account.followee_ids == []
        assert user_account.followees == []
        assert user_account.follower_ids == []
        assert user_account.followers == []

    user_accounts_more = await user_account_repository.read_by_usernames_async(
        usernames=set(usernames + ["username2"])
    )

    assert len(user_accounts_more) == len(usernames)
    for user_account, username, email, entity_id, user_id in zip(
        user_accounts_more, usernames, emails, entity_ids, user_ids
    ):
        assert user_account is not None
        assert user_account.id == entity_id
        assert user_account.user_id == user_id
        assert user_account.username == username
        assert user_account.hashed_password == hashed_password
        assert user_account.refresh_token is None
        assert user_account.nickname == nickname
        assert user_account.birth_date == birth_date.replace(tzinfo=None)
        assert user_account.gender == gender
        assert user_account.email == email
        assert user_account.email_verified is False
        assert user_account.followee_ids == []
        assert user_account.followees == []
        assert user_account.follower_ids == []
        assert user_account.followers == []

    user_accounts_less = await user_account_repository.read_by_usernames_async(
        usernames=set(usernames[:1])
    )

    assert len(user_accounts_less) == 1
    for user_account, username, email, entity_id, user_id in zip(
        user_accounts_less, usernames[:1], emails[:1], entity_ids[:1], user_ids[:1]
    ):
        assert user_account is not None
        assert user_account.id == entity_id
        assert user_account.user_id == user_id
        assert user_account.username == username
        assert user_account.hashed_password == hashed_password
        assert user_account.refresh_token is None
        assert user_account.nickname == nickname
        assert user_account.birth_date == birth_date.replace(tzinfo=None)
        assert user_account.gender == gender
        assert user_account.email == email
        assert user_account.email_verified is False
        assert user_account.followee_ids == []
        assert user_account.followees == []
        assert user_account.follower_ids == []
        assert user_account.followers == []


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
    assert user_account.id == entity_id
    assert user_account.user_id == user_id
    assert user_account.username == username
    assert user_account.hashed_password == hashed_password
    assert user_account.refresh_token is None
    assert user_account.nickname == nickname
    assert user_account.birth_date == birth_date.replace(tzinfo=None)
    assert user_account.gender == gender
    assert user_account.email == email
    assert user_account.email_verified is False
    assert user_account.followee_ids == []
    assert user_account.followees == []
    assert user_account.follower_ids == []
    assert user_account.followers == []

    non_existent_user_account = (
        await user_account_repository.read_by_email_or_none_async(
            email="non_existent" + email
        )
    )

    assert non_existent_user_account is None


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
async def test_read_with_followees_by_id_or_none_async(
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

    entity_ids = [generate_uuid() for _ in range(len(usernames))]
    user_ids = [await SequenceUserId.id_generator(uow) for _ in range(len(usernames))]

    await user_account_repository.create_user_account_async(
        entity_id=entity_ids[0],
        user_id=user_ids[0],
        username=usernames[0],
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email=emails[0],
        followee_ids=set(),
        follower_ids=set(),
        refresh_token=None,
        nickname=nickname,
    )
    await user_account_repository.create_user_account_async(
        entity_id=entity_ids[1],
        user_id=user_ids[1],
        username=usernames[1],
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email=emails[1],
        followee_ids={entity_ids[0]},
        follower_ids=set(),
        refresh_token=None,
        nickname=nickname,
    )

    user1 = await user_account_repository.read_with_followees_by_id_or_none_async(
        record_id=entity_ids[1]
    )

    assert user1 is not None
    assert len(user1.followees) == 1
    assert len(user1.followers) == 0
    assert user1.followees[0].id == entity_ids[0]
    assert user1.followees[0].user_id == user_ids[0]
    assert user1.followees[0].username == usernames[0]
    assert user1.followees[0].hashed_password == hashed_password
    assert user1.followees[0].refresh_token is None
    assert user1.followees[0].nickname == nickname
    assert user1.followees[0].birth_date == birth_date.replace(tzinfo=None)
    assert user1.followees[0].gender == gender
    assert user1.followees[0].email == emails[0]
    assert user1.followees[0].email_verified is False
    assert user1.followees[0].followee_ids == []
    assert user1.followees[0].followees == []
    assert user1.followees[0].follower_ids == []
    assert user1.followees[0].followers == []

    user0 = await user_account_repository.read_with_followers_by_id_or_none_async(
        record_id=entity_ids[0]
    )

    assert user0 is not None
    assert len(user0.followees) == 0
    assert len(user0.followers) == 1
    assert user0.followers[0].id == entity_ids[1]
    assert user0.followers[0].user_id == user_ids[1]
    assert user0.followers[0].username == usernames[1]
    assert user0.followers[0].hashed_password == hashed_password
    assert user0.followers[0].refresh_token is None
    assert user0.followers[0].nickname == nickname
    assert user0.followers[0].birth_date == birth_date.replace(tzinfo=None)
    assert user0.followers[0].gender == gender
    assert user0.followers[0].email == emails[1]
    assert user0.followers[0].email_verified is False
    assert user0.followers[0].followee_ids == []
    assert user0.followers[0].followees == []
    assert user0.followers[0].follower_ids == []
    assert user0.followers[0].followers == []


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
async def test_read_with_followers_by_id_or_none_async(
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

    entity_ids = [generate_uuid() for _ in range(len(usernames))]
    user_ids = [await SequenceUserId.id_generator(uow) for _ in range(len(usernames))]

    await user_account_repository.create_user_account_async(
        entity_id=entity_ids[0],
        user_id=user_ids[0],
        username=usernames[0],
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email=emails[0],
        followee_ids=set(),
        follower_ids=set(),
        refresh_token=None,
        nickname=nickname,
    )
    await user_account_repository.create_user_account_async(
        entity_id=entity_ids[1],
        user_id=user_ids[1],
        username=usernames[1],
        hashed_password=hashed_password,
        birth_date=birth_date,
        gender=gender,
        email=emails[1],
        followee_ids=set(),
        follower_ids={entity_ids[0]},
        refresh_token=None,
        nickname=nickname,
    )

    user1 = await user_account_repository.read_with_followers_by_id_or_none_async(
        record_id=entity_ids[1]
    )

    assert user1 is not None
    assert len(user1.followees) == 0
    assert len(user1.followers) == 1
    assert user1.followers[0].id == entity_ids[0]
    assert user1.followers[0].user_id == user_ids[0]
    assert user1.followers[0].username == usernames[0]
    assert user1.followers[0].hashed_password == hashed_password
    assert user1.followers[0].refresh_token is None
    assert user1.followers[0].nickname == nickname
    assert user1.followers[0].birth_date == birth_date.replace(tzinfo=None)
    assert user1.followers[0].gender == gender
    assert user1.followers[0].email == emails[0]
    assert user1.followers[0].email_verified is False
    assert user1.followers[0].followee_ids == []
    assert user1.followers[0].followees == []
    assert user1.followers[0].follower_ids == []
    assert user1.followers[0].followers == []

    user0 = await user_account_repository.read_with_followees_by_id_or_none_async(
        record_id=entity_ids[0]
    )

    assert user0 is not None
    assert len(user0.followees) == 1
    assert len(user0.followers) == 0
    assert user0.followees[0].id == entity_ids[1]
    assert user0.followees[0].user_id == user_ids[1]
    assert user0.followees[0].username == usernames[1]
    assert user0.followees[0].hashed_password == hashed_password
    assert user0.followees[0].refresh_token is None
    assert user0.followees[0].nickname == nickname
    assert user0.followees[0].birth_date == birth_date.replace(tzinfo=None)
    assert user0.followees[0].gender == gender
    assert user0.followees[0].email == emails[1]
    assert user0.followees[0].email_verified is False
    assert user0.followees[0].followee_ids == []
    assert user0.followees[0].followees == []
    assert user0.followees[0].follower_ids == []
    assert user0.followees[0].followers == []
