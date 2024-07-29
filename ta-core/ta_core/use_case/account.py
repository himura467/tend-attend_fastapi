from dataclasses import dataclass

from ta_core.cryptography.hash import PasswordHasher
from ta_core.dtos.account import CreateGuestAccountResponse, CreateHostAccountResponse
from ta_core.error.error_code import ErrorCode
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.models.commons.account import (
    GuestAccount,
    HostAccount,
)
from ta_core.infrastructure.sqlalchemy.models.sequences.sequence import SequenceUserId
from ta_core.infrastructure.sqlalchemy.repositories.account import (
    GuestAccountRepository,
    HostAccountRepository,
)
from ta_core.use_case.unit_of_work_base import IUnitOfWork
from ta_core.utils.uuid import generate_uuid


@dataclass(frozen=True)
class AccountUseCase:
    uow: IUnitOfWork

    _password_hasher = PasswordHasher()

    @rollbackable
    async def create_host_account_async(
        self, host_name: str, password: str, email: str
    ) -> CreateHostAccountResponse:
        host_account_repository = HostAccountRepository(self.uow, HostAccount)  # type: ignore

        host_account = await host_account_repository.create_host_account_async(
            entity_id=generate_uuid(),
            host_name=host_name,
            hashed_password=self._password_hasher.get_password_hash(password),
            email=email,
        )
        if host_account is None:
            return CreateHostAccountResponse(
                error_codes=(ErrorCode.HOST_NAME_OR_EMAIL_ALREADY_REGISTERED,)
            )

        return CreateHostAccountResponse(error_codes=())

    @rollbackable
    async def create_guest_account_async(
        self,
        guest_first_name: str,
        guest_last_name: str,
        guest_nickname: str | None,
        password: str,
        host_name: str,
    ) -> CreateGuestAccountResponse:
        host_account_repository = HostAccountRepository(self.uow, HostAccount)  # type: ignore
        guest_account_repository = GuestAccountRepository(self.uow, GuestAccount)  # type: ignore

        user_id = await SequenceUserId.id_generator(self.uow)

        host_account = await host_account_repository.read_by_host_name_or_none_async(
            host_name=host_name
        )
        if host_account is None:
            return CreateGuestAccountResponse(
                error_codes=(ErrorCode.HOST_NAME_NOT_EXIST,)
            )

        guest_account = await guest_account_repository.create_guest_account_async(
            entity_id=generate_uuid(),
            guest_first_name=guest_first_name,
            guest_last_name=guest_last_name,
            guest_nickname=guest_nickname,
            hashed_password=self._password_hasher.get_password_hash(password),
            user_id=user_id,
            host_id=host_account.id,
        )
        if guest_account is None:
            return CreateGuestAccountResponse(
                error_codes=(ErrorCode.GUEST_NAME_ALREADY_REGISTERED,)
            )

        return CreateGuestAccountResponse(error_codes=())
