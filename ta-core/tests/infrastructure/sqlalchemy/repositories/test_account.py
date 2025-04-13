from datetime import datetime
from typing import Any
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
    "accounts_by_user",
    [
        {
            0: {  # ユーザー 0
                "username": "username0",
                "hashed_password": "hashed_password",
                "birth_date": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                "gender": Gender.MALE,
                "email": "test@example.com",
                "nickname": None,
            },
        },
    ],
)
async def test_read_by_username_or_none_async(
    test_session: AsyncSession,
    accounts_by_user: dict[int, dict[str, Any]],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    entity_ids = {}
    user_ids = {}
    for user_index, account_data in accounts_by_user.items():
        entity_id = generate_uuid()
        user_id = await SequenceUserId.id_generator(uow)
        entity_ids[user_index] = entity_id
        user_ids[user_index] = user_id

        await user_account_repository.create_user_account_async(
            entity_id=entity_id,
            user_id=user_id,
            username=account_data["username"],
            hashed_password=account_data["hashed_password"],
            birth_date=account_data["birth_date"],
            gender=account_data["gender"],
            email=account_data["email"],
            followee_ids=set(),
            follower_ids=set(),
            refresh_token=None,
            nickname=account_data["nickname"],
        )

    test_user_index = 0
    test_account_data = accounts_by_user[test_user_index]
    user_account = await user_account_repository.read_by_username_or_none_async(
        username=test_account_data["username"]
    )

    assert user_account is not None
    assert user_account.id == entity_ids[test_user_index]
    assert user_account.user_id == user_ids[test_user_index]
    assert user_account.username == test_account_data["username"]
    assert user_account.hashed_password == test_account_data["hashed_password"]
    assert user_account.refresh_token is None
    assert user_account.nickname == test_account_data["nickname"]
    assert user_account.birth_date == test_account_data["birth_date"].replace(
        tzinfo=None
    )
    assert user_account.gender == test_account_data["gender"]
    assert user_account.email == test_account_data["email"]
    assert user_account.email_verified is False
    assert user_account.followee_ids == []
    assert user_account.followees == []
    assert user_account.follower_ids == []
    assert user_account.followers == []

    non_existent_user_account = (
        await user_account_repository.read_by_username_or_none_async(
            username="non_existent_username"
        )
    )

    assert non_existent_user_account is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "accounts_by_user",
    [
        {
            0: {  # ユーザー 0
                "username": "username0",
                "hashed_password": "hashed_password",
                "birth_date": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                "gender": Gender.MALE,
                "email": "user0@example.com",
                "nickname": None,
            },
            1: {  # ユーザー 1
                "username": "username1",
                "hashed_password": "hashed_password",
                "birth_date": datetime(2010, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                "gender": Gender.FEMALE,
                "email": "user1@example.com",
                "nickname": None,
            },
        },
    ],
)
async def test_read_by_usernames_async(
    test_session: AsyncSession,
    accounts_by_user: dict[int, dict[str, Any]],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    entity_ids = {}
    user_ids = {}
    created_accounts = {}
    for user_index, account_data in accounts_by_user.items():
        entity_id = generate_uuid()
        user_id = await SequenceUserId.id_generator(uow)
        entity_ids[user_index] = entity_id
        user_ids[user_index] = user_id
        created_accounts[user_index] = account_data

        await user_account_repository.create_user_account_async(
            entity_id=entity_id,
            user_id=user_id,
            username=account_data["username"],
            hashed_password=account_data["hashed_password"],
            birth_date=account_data["birth_date"],
            gender=account_data["gender"],
            email=account_data["email"],
            followee_ids=set(),
            follower_ids=set(),
            refresh_token=None,
            nickname=account_data["nickname"],
        )

    usernames = {account_data["username"] for account_data in accounts_by_user.values()}
    user_accounts = await user_account_repository.read_by_usernames_async(
        usernames=usernames
    )
    assert len(user_accounts) == len(accounts_by_user)

    for user_account in user_accounts:
        matched = False
        for user_index, account_data in accounts_by_user.items():
            if user_account.username == account_data["username"]:
                matched = True
                assert user_account.id == entity_ids[user_index]
                assert user_account.user_id == user_ids[user_index]
                assert user_account.hashed_password == account_data["hashed_password"]
                assert user_account.refresh_token is None
                assert user_account.nickname == account_data["nickname"]
                assert user_account.birth_date == account_data["birth_date"].replace(
                    tzinfo=None
                )
                assert user_account.gender == account_data["gender"]
                assert user_account.email == account_data["email"]
                assert user_account.email_verified is False
                assert user_account.followee_ids == []
                assert user_account.followees == []
                assert user_account.follower_ids == []
                assert user_account.followers == []
                break
        assert matched, f"User account {user_account.username} not found in test data"

    usernames_with_non_existent = usernames | {"non_existent_username"}
    user_accounts_more = await user_account_repository.read_by_usernames_async(
        usernames=usernames_with_non_existent
    )
    assert len(user_accounts_more) == len(accounts_by_user)

    first_username = next(iter(accounts_by_user.values()))["username"]
    user_accounts_less = await user_account_repository.read_by_usernames_async(
        usernames={first_username}
    )
    assert len(user_accounts_less) == 1
    assert user_accounts_less[0].username == first_username


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "accounts_by_user",
    [
        {
            0: {  # ユーザー 0
                "username": "username0",
                "hashed_password": "hashed_password",
                "birth_date": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                "gender": Gender.MALE,
                "email": "test@example.com",
                "nickname": None,
            },
        },
    ],
)
async def test_read_by_email_or_none_async(
    test_session: AsyncSession,
    accounts_by_user: dict[int, dict[str, Any]],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    entity_ids = {}
    user_ids = {}
    for user_index, account_data in accounts_by_user.items():
        entity_id = generate_uuid()
        user_id = await SequenceUserId.id_generator(uow)
        entity_ids[user_index] = entity_id
        user_ids[user_index] = user_id

        await user_account_repository.create_user_account_async(
            entity_id=entity_id,
            user_id=user_id,
            username=account_data["username"],
            hashed_password=account_data["hashed_password"],
            birth_date=account_data["birth_date"],
            gender=account_data["gender"],
            email=account_data["email"],
            followee_ids=set(),
            follower_ids=set(),
            refresh_token=None,
            nickname=account_data["nickname"],
        )

    test_user_index = 0
    test_account_data = accounts_by_user[test_user_index]
    user_account = await user_account_repository.read_by_email_or_none_async(
        email=test_account_data["email"]
    )

    assert user_account is not None
    assert user_account.id == entity_ids[test_user_index]
    assert user_account.user_id == user_ids[test_user_index]
    assert user_account.username == test_account_data["username"]
    assert user_account.hashed_password == test_account_data["hashed_password"]
    assert user_account.refresh_token is None
    assert user_account.nickname == test_account_data["nickname"]
    assert user_account.birth_date == test_account_data["birth_date"].replace(
        tzinfo=None
    )
    assert user_account.gender == test_account_data["gender"]
    assert user_account.email == test_account_data["email"]
    assert user_account.email_verified is False
    assert user_account.followee_ids == []
    assert user_account.followees == []
    assert user_account.follower_ids == []
    assert user_account.followers == []

    non_existent_user_account = (
        await user_account_repository.read_by_email_or_none_async(
            email="non_existent@example.com"
        )
    )

    assert non_existent_user_account is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "accounts_by_user",
    [
        {
            0: {  # フォロイー
                "username": "username0",
                "hashed_password": "hashed_password",
                "birth_date": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                "gender": Gender.MALE,
                "email": "user0@example.com",
                "nickname": None,
            },
            1: {  # フォロワー
                "username": "username1",
                "hashed_password": "hashed_password",
                "birth_date": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                "gender": Gender.MALE,
                "email": "user1@example.com",
                "nickname": None,
                "follows": [0],  # ユーザー 0 をフォロー
            },
        },
    ],
)
async def test_read_with_followees_by_id_or_none_async(
    test_session: AsyncSession,
    accounts_by_user: dict[int, dict[str, Any]],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    entity_ids = {}
    user_ids = {}
    for user_index, account_data in accounts_by_user.items():
        entity_id = generate_uuid()
        user_id = await SequenceUserId.id_generator(uow)
        entity_ids[user_index] = entity_id
        user_ids[user_index] = user_id

    for user_index, account_data in accounts_by_user.items():
        followee_ids = set()
        if "follows" in account_data:
            followee_ids = {
                entity_ids[followed_index] for followed_index in account_data["follows"]
            }

        await user_account_repository.create_user_account_async(
            entity_id=entity_ids[user_index],
            user_id=user_ids[user_index],
            username=account_data["username"],
            hashed_password=account_data["hashed_password"],
            birth_date=account_data["birth_date"],
            gender=account_data["gender"],
            email=account_data["email"],
            followee_ids=followee_ids,
            follower_ids=set(),
            refresh_token=None,
            nickname=account_data["nickname"],
        )

    followee_user_account = (
        await user_account_repository.read_with_followers_by_id_or_none_async(
            record_id=entity_ids[0]
        )
    )

    assert followee_user_account is not None
    assert len(followee_user_account.followees) == 0
    assert len(followee_user_account.followers) == 1
    follower = followee_user_account.followers[0]
    assert follower.id == entity_ids[1]
    assert follower.user_id == user_ids[1]
    assert follower.username == accounts_by_user[1]["username"]
    assert follower.hashed_password == accounts_by_user[1]["hashed_password"]
    assert follower.refresh_token is None
    assert follower.nickname == accounts_by_user[1]["nickname"]
    assert follower.birth_date == accounts_by_user[1]["birth_date"].replace(tzinfo=None)
    assert follower.gender == accounts_by_user[1]["gender"]
    assert follower.email == accounts_by_user[1]["email"]
    assert follower.email_verified is False
    assert follower.followee_ids == []
    assert follower.followees == []
    assert follower.follower_ids == []
    assert follower.followers == []

    follower_user_account = (
        await user_account_repository.read_with_followees_by_id_or_none_async(
            record_id=entity_ids[1]
        )
    )

    assert follower_user_account is not None
    assert len(follower_user_account.followees) == 1
    assert len(follower_user_account.followers) == 0
    followee = follower_user_account.followees[0]
    assert followee.id == entity_ids[0]
    assert followee.user_id == user_ids[0]
    assert followee.username == accounts_by_user[0]["username"]
    assert followee.hashed_password == accounts_by_user[0]["hashed_password"]
    assert followee.refresh_token is None
    assert followee.nickname == accounts_by_user[0]["nickname"]
    assert followee.birth_date == accounts_by_user[0]["birth_date"].replace(tzinfo=None)
    assert followee.gender == accounts_by_user[0]["gender"]
    assert followee.email == accounts_by_user[0]["email"]
    assert followee.email_verified is False
    assert followee.followee_ids == []
    assert followee.followees == []
    assert followee.follower_ids == []
    assert followee.followers == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "accounts_by_user",
    [
        {
            0: {  # フォロイー
                "username": "username0",
                "hashed_password": "hashed_password",
                "birth_date": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                "gender": Gender.MALE,
                "email": "user0@example.com",
                "nickname": None,
            },
            1: {  # フォロワー
                "username": "username1",
                "hashed_password": "hashed_password",
                "birth_date": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                "gender": Gender.MALE,
                "email": "user1@example.com",
                "nickname": None,
                "follows": [0],  # ユーザー 0 をフォロー
            },
        },
    ],
)
async def test_read_with_followers_by_id_or_none_async(
    test_session: AsyncSession,
    accounts_by_user: dict[int, dict[str, Any]],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    user_account_repository = UserAccountRepository(uow)

    entity_ids = {}
    user_ids = {}
    for user_index, account_data in accounts_by_user.items():
        entity_id = generate_uuid()
        user_id = await SequenceUserId.id_generator(uow)
        entity_ids[user_index] = entity_id
        user_ids[user_index] = user_id

    for user_index, account_data in accounts_by_user.items():
        followee_ids = set()
        if "follows" in account_data:
            followee_ids = {
                entity_ids[followed_index] for followed_index in account_data["follows"]
            }

        await user_account_repository.create_user_account_async(
            entity_id=entity_ids[user_index],
            user_id=user_ids[user_index],
            username=account_data["username"],
            hashed_password=account_data["hashed_password"],
            birth_date=account_data["birth_date"],
            gender=account_data["gender"],
            email=account_data["email"],
            followee_ids=followee_ids,
            follower_ids=set(),
            refresh_token=None,
            nickname=account_data["nickname"],
        )

    followee_user_account = (
        await user_account_repository.read_with_followers_by_id_or_none_async(
            record_id=entity_ids[0]
        )
    )

    assert followee_user_account is not None
    assert len(followee_user_account.followees) == 0
    assert len(followee_user_account.followers) == 1
    follower = followee_user_account.followers[0]
    assert follower.id == entity_ids[1]
    assert follower.user_id == user_ids[1]
    assert follower.username == accounts_by_user[1]["username"]
    assert follower.hashed_password == accounts_by_user[1]["hashed_password"]
    assert follower.refresh_token is None
    assert follower.nickname == accounts_by_user[1]["nickname"]
    assert follower.birth_date == accounts_by_user[1]["birth_date"].replace(tzinfo=None)
    assert follower.gender == accounts_by_user[1]["gender"]
    assert follower.email == accounts_by_user[1]["email"]
    assert follower.email_verified is False
    assert follower.followee_ids == []
    assert follower.followees == []
    assert follower.follower_ids == []
    assert follower.followers == []

    follower_user_account = (
        await user_account_repository.read_with_followees_by_id_or_none_async(
            record_id=entity_ids[1]
        )
    )

    assert follower_user_account is not None
    assert len(follower_user_account.followees) == 1
    assert len(follower_user_account.followers) == 0
    followee = follower_user_account.followees[0]
    assert followee.id == entity_ids[0]
    assert followee.user_id == user_ids[0]
    assert followee.username == accounts_by_user[0]["username"]
    assert followee.hashed_password == accounts_by_user[0]["hashed_password"]
    assert followee.refresh_token is None
    assert followee.nickname == accounts_by_user[0]["nickname"]
    assert followee.birth_date == accounts_by_user[0]["birth_date"].replace(tzinfo=None)
    assert followee.gender == accounts_by_user[0]["gender"]
    assert followee.email == accounts_by_user[0]["email"]
    assert followee.email_verified is False
    assert followee.followee_ids == []
    assert followee.followees == []
    assert followee.follower_ids == []
    assert followee.followers == []
