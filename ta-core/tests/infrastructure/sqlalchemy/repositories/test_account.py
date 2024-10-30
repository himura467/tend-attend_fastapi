import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic.networks import EmailStr

from ta_core.infrastructure.sqlalchemy.repositories.account import (
    GuestAccountRepository,
    HostAccountRepository,
)
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.utils.uuid import generate_uuid


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host_name, hashed_password, email",
    [
        ("host_name", "hashed_password", "test@example.com"),
    ],
)
async def test_create_host_account_async(
    test_session: AsyncSession, host_name: str, hashed_password: str, email: EmailStr
):
    uow = SqlalchemyUnitOfWork(session=test_session)
    host_account_repository = HostAccountRepository(uow)

    host_account = await host_account_repository.create_host_account_async(
        entity_id=generate_uuid(),
        host_name=host_name,
        hashed_password=hashed_password,
        email=email,
    )

    assert host_account is not None
    assert host_account.host_name == host_name
    assert host_account.hashed_password == hashed_password
    assert host_account.email == email


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host_name, hashed_password, email",
    [
        ("host_name", "hashed_password", "test@example.com"),
    ],
)
async def test_read_by_host_name_or_none_async(
    test_session: AsyncSession, host_name: str, hashed_password: str, email: EmailStr
):
    uow = SqlalchemyUnitOfWork(session=test_session)
    host_account_repository = HostAccountRepository(uow)

    await host_account_repository.create_host_account_async(
        entity_id=generate_uuid(),
        host_name=host_name,
        hashed_password=hashed_password,
        email=email,
    )
    host_account = await host_account_repository.read_by_host_name_or_none_async(
        host_name=host_name
    )

    assert host_account is not None
    assert host_account.host_name == host_name
    assert host_account.hashed_password == hashed_password
    assert host_account.email == email


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host_name, hashed_password, email",
    [
        ("host_name", "hashed_password", "test@example.com"),
    ],
)
async def test_read_by_email_or_none_async(
    test_session: AsyncSession, host_name: str, hashed_password: str, email: EmailStr
):
    uow = SqlalchemyUnitOfWork(session=test_session)
    host_account_repository = HostAccountRepository(uow)

    await host_account_repository.create_host_account_async(
        entity_id=generate_uuid(),
        host_name=host_name,
        hashed_password=hashed_password,
        email=email,
    )
    host_account = await host_account_repository.read_by_email_or_none_async(
        email=email
    )

    assert host_account is not None
    assert host_account.host_name == host_name
    assert host_account.hashed_password == hashed_password
    assert host_account.email == email


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host_name, host_hashed_password, email, guest_first_name, guest_last_name, guest_nickname, guest_hashed_password, user_id",
    [
        (
            "host_name",
            "host_hashed_password",
            "test@example.com",
            "guest_first_name",
            "guest_last_name",
            "guest_nickname",
            "guest_hashed_password",
            0,
        ),
    ],
)
async def test_create_guest_account_async(
    test_session: AsyncSession,
    host_name: str,
    host_hashed_password: str,
    email: EmailStr,
    guest_first_name: str,
    guest_last_name: str,
    guest_nickname: str,
    guest_hashed_password: str,
    user_id: int,
):
    uow = SqlalchemyUnitOfWork(session=test_session)
    host_account_repository = HostAccountRepository(uow)
    guest_account_repository = GuestAccountRepository(uow)

    host_account = await host_account_repository.create_host_account_async(
        entity_id=generate_uuid(),
        host_name=host_name,
        hashed_password=host_hashed_password,
        email=email,
    )
    assert host_account is not None
    guest_account = await guest_account_repository.create_guest_account_async(
        entity_id=generate_uuid(),
        guest_first_name=guest_first_name,
        guest_last_name=guest_last_name,
        guest_nickname=guest_nickname,
        hashed_password=guest_hashed_password,
        user_id=user_id,
        host_id=host_account.id,
    )

    assert guest_account is not None
    assert guest_account.guest_first_name == guest_first_name
    assert guest_account.guest_last_name == guest_last_name
    assert guest_account.guest_nickname == guest_nickname
    assert guest_account.hashed_password == guest_hashed_password
    assert guest_account.user_id == user_id
    assert guest_account.host_id == host_account.id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host_name, host_hashed_password, email, guest_first_name, guest_last_name, guest_nickname, guest_hashed_password, user_id",
    [
        (
            "host_name",
            "host_hashed_password",
            "test@example.com",
            "guest_first_name",
            "guest_last_name",
            "guest_nickname",
            "guest_hashed_password",
            0,
        ),
    ],
)
async def test_read_by_guest_name_and_host_id_or_none_async(
    test_session: AsyncSession,
    host_name: str,
    host_hashed_password: str,
    email: EmailStr,
    guest_first_name: str,
    guest_last_name: str,
    guest_nickname: str,
    guest_hashed_password: str,
    user_id: int,
):
    uow = SqlalchemyUnitOfWork(session=test_session)
    host_account_repository = HostAccountRepository(uow)
    guest_account_repository = GuestAccountRepository(uow)

    host_account = await host_account_repository.create_host_account_async(
        entity_id=generate_uuid(),
        host_name=host_name,
        hashed_password=host_hashed_password,
        email=email,
    )
    assert host_account is not None
    await guest_account_repository.create_guest_account_async(
        entity_id=generate_uuid(),
        guest_first_name=guest_first_name,
        guest_last_name=guest_last_name,
        guest_nickname=guest_nickname,
        hashed_password=guest_hashed_password,
        user_id=user_id,
        host_id=host_account.id,
    )
    guest_account = (
        await guest_account_repository.read_by_guest_name_and_host_id_or_none_async(
            guest_first_name=guest_first_name,
            guest_last_name=guest_last_name,
            guest_nickname=guest_nickname,
            host_id=host_account.id,
        )
    )

    assert guest_account is not None
    assert guest_account.guest_first_name == guest_first_name
    assert guest_account.guest_last_name == guest_last_name
    assert guest_account.guest_nickname == guest_nickname
    assert guest_account.hashed_password == guest_hashed_password
    assert guest_account.user_id == user_id
    assert guest_account.host_id == host_account.id
