from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ta_core.dtos.verify import (
    RequestEmailVerificationRequest,
    RequestEmailVerificationResponse,
)
from ta_core.infrastructure.sqlalchemy.db import get_db_async
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.use_case.verify import VerifyUseCase

router = APIRouter()


@router.post(
    path="/email",
    name="Request Email Verification",
    response_model=RequestEmailVerificationResponse,
)
async def request_email_verification(
    req: RequestEmailVerificationRequest,
    session: AsyncSession = Depends(get_db_async),
) -> RequestEmailVerificationResponse:
    host_email = req.host_email

    uow = SqlalchemyUnitOfWork(session=session)
    use_case = VerifyUseCase(uow=uow)

    return await use_case.request_email_verification_async(host_email=host_email)
