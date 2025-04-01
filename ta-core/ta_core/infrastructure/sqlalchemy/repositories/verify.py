from datetime import datetime

from pydantic.networks import EmailStr

from ta_core.domain.entities.verify import EmailVerification as EmailVerificationEntity
from ta_core.infrastructure.sqlalchemy.models.commons.verify import EmailVerification
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository
from ta_core.utils.uuid import UUID


class EmailVerificationRepository(
    AbstractRepository[EmailVerificationEntity, EmailVerification]
):
    @property
    def _model(self) -> type[EmailVerification]:
        return EmailVerification

    async def create_email_verification_async(
        self,
        entity_id: UUID,
        email: EmailStr,
        verification_token: UUID,
        token_expires_at: datetime,
    ) -> EmailVerificationEntity | None:
        email_verification = EmailVerificationEntity(
            entity_id=entity_id,
            email=email,
            verification_token=verification_token,
            token_expires_at=token_expires_at,
        )
        return await self.create_async(email_verification)

    async def read_latest_by_email_or_none_async(
        self, email: EmailStr
    ) -> EmailVerificationEntity | None:
        email_verifications = await self.read_order_by_limit_async(
            where=(self._model.email == email,),
            order_by=self._model.token_expires_at.desc(),
            limit=1,
        )
        return email_verifications[0] if email_verifications else None
