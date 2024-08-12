from dataclasses import dataclass
from datetime import datetime, timedelta

from pydantic.networks import EmailStr

from ta_core.dtos.verify import RequestEmailVerificationResponse
from ta_core.error.error_code import ErrorCode
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.repositories.account import HostAccountRepository
from ta_core.infrastructure.sqlalchemy.repositories.verify import (
    HostVerificationRepository,
)
from ta_core.use_case.unit_of_work_base import IUnitOfWork
from ta_core.utils.smtp import send_verification_email_async
from ta_core.utils.uuid import generate_uuid


@dataclass(frozen=True)
class VerifyUseCase:
    uow: IUnitOfWork

    _TOKEN_EXPIRES = timedelta(minutes=5)

    @rollbackable
    async def request_email_verification_async(
        self, host_email: EmailStr
    ) -> RequestEmailVerificationResponse:
        host_account_repository = HostAccountRepository(self.uow)
        host_verification_repository = HostVerificationRepository(self.uow)

        host_account = await host_account_repository.read_by_email_or_none_async(
            host_email
        )
        if host_account is None:
            return RequestEmailVerificationResponse(
                error_codes=(ErrorCode.HOST_EMAIL_NOT_EXIST,)
            )
        if host_account.user_id is not None:
            return RequestEmailVerificationResponse(
                error_codes=(ErrorCode.HOST_EMAIL_ALREADY_VERIFIED,)
            )

        verification_token = generate_uuid()
        token_expires_at = datetime.utcnow() + self._TOKEN_EXPIRES
        host_verification = (
            await host_verification_repository.create_host_verification_async(
                entity_id=generate_uuid(),
                host_email=host_email,
                verification_token=verification_token,
                token_expires_at=token_expires_at,
            )
        )
        if host_verification is None:
            raise Exception("Failed to create host verification")

        verification_link = f"https://example.com/verify?token={verification_token}"

        error_codes = await send_verification_email_async(host_email, verification_link)
        return RequestEmailVerificationResponse(error_codes=error_codes)
