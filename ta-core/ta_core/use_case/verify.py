from dataclasses import dataclass

from pydantic.networks import EmailStr

from ta_core.dtos.verify import RequestEmailVerificationResponse
from ta_core.error.error_code import ErrorCode
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.models.commons.account import HostAccount
from ta_core.infrastructure.sqlalchemy.repositories.account import HostAccountRepository
from ta_core.use_case.unit_of_work_base import IUnitOfWork
from ta_core.utils.smtp import send_verification_email_async
from ta_core.utils.uuid import generate_uuid


@dataclass(frozen=True)
class VerifyUseCase:
    uow: IUnitOfWork

    @rollbackable
    async def request_email_verification_async(
        self, host_email: EmailStr
    ) -> RequestEmailVerificationResponse:
        host_account_repository = HostAccountRepository(self.uow, HostAccount)  # type: ignore

        host_account = await host_account_repository.read_by_email_or_none_async(
            host_email
        )
        if host_account is None:
            return RequestEmailVerificationResponse(
                error_codes=(ErrorCode.HOST_EMAIL_NOT_EXIST,)
            )

        verification_token = generate_uuid()
        # TODO: save verification token to database

        verification_link = f"https://example.com/verify?token={verification_token}"
        host_email = host_account.email

        error_codes = await send_verification_email_async(host_email, verification_link)
        return RequestEmailVerificationResponse(error_codes=error_codes)
