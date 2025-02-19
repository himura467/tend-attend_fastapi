from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from ta_core.dtos.verify import (
    RequestEmailVerificationRequest,
    RequestEmailVerificationResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.verify import VerifyUseCase

router = APIRouter()


@router.post(
    path="/email/register",
    name="Request Email Verification",
    response_model=RequestEmailVerificationResponse,
)
async def request_email_verification(
    req: RequestEmailVerificationRequest,
    session: AsyncSession = Depends(get_db_async),
) -> RequestEmailVerificationResponse:
    email = req.email

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = VerifyUseCase(uow=uow)

    return await use_case.request_email_verification_async(email=email)


@router.post(
    path="/email",
    name="Verify Email",
    response_model=VerifyEmailResponse,
)
async def verify_email(
    req: VerifyEmailRequest,
    session: AsyncSession = Depends(get_db_async),
) -> VerifyEmailResponse:
    email = req.email
    verification_token = req.verification_token

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = VerifyUseCase(uow=uow)

    return await use_case.verify_email_async(
        email=email, verification_token=verification_token
    )
