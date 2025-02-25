from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pydantic.networks import EmailStr

from ta_core.dtos.verify import RequestEmailVerificationResponse, VerifyEmailResponse
from ta_core.error.error_code import ErrorCode
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.repositories.account import UserAccountRepository
from ta_core.infrastructure.sqlalchemy.repositories.verify import (
    EmailVerificationRepository,
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
        self, email: EmailStr
    ) -> RequestEmailVerificationResponse:
        user_account_repository = UserAccountRepository(self.uow)
        email_verification_repository = EmailVerificationRepository(self.uow)

        user_account = await user_account_repository.read_by_email_or_none_async(email)
        if user_account is None:
            return RequestEmailVerificationResponse(
                error_codes=(ErrorCode.EMAIL_NOT_REGISTERED,)
            )
        if user_account.email_verified:
            return RequestEmailVerificationResponse(
                error_codes=(ErrorCode.EMAIL_ALREADY_VERIFIED,)
            )

        verification_token = generate_uuid()
        token_expires_at = datetime.now(ZoneInfo("UTC")) + self._TOKEN_EXPIRES
        email_verification = (
            await email_verification_repository.create_email_verification_async(
                entity_id=generate_uuid(),
                email=email,
                verification_token=verification_token,
                token_expires_at=token_expires_at,
            )
        )
        if email_verification is None:
            raise Exception("Failed to create email verification")

        verification_link = f"https://example.com/verify?token={verification_token}"

        error_codes = await send_verification_email_async(email, verification_link)
        return RequestEmailVerificationResponse(error_codes=error_codes)

    @rollbackable
    async def verify_email_async(
        self, email: EmailStr, verification_token: str
    ) -> VerifyEmailResponse:
        user_account_repository = UserAccountRepository(self.uow)
        email_verification_repository = EmailVerificationRepository(self.uow)

        user_account = await user_account_repository.read_by_email_or_none_async(email)
        if user_account is None:
            return VerifyEmailResponse(error_codes=(ErrorCode.EMAIL_NOT_REGISTERED,))
        if user_account.email_verified:
            return VerifyEmailResponse(error_codes=(ErrorCode.EMAIL_ALREADY_VERIFIED,))

        email_verification = (
            await email_verification_repository.read_latest_by_email_or_none_async(
                email
            )
        )
        if email_verification is None:
            return VerifyEmailResponse(
                error_codes=(ErrorCode.VERIFICATION_TOKEN_NOT_EXIST,)
            )
        if email_verification.verification_token != verification_token:
            return VerifyEmailResponse(
                error_codes=(ErrorCode.VERIFICATION_TOKEN_INVALID,)
            )
        if email_verification.token_expires_at < datetime.now(ZoneInfo("UTC")):
            return VerifyEmailResponse(
                error_codes=(ErrorCode.VERIFICATION_TOKEN_EXPIRED,)
            )

        user_account.email_verified = True
        await user_account_repository.update_async(user_account)

        return VerifyEmailResponse(error_codes=())
