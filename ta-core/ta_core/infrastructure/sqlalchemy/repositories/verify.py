from datetime import datetime

from pydantic.networks import EmailStr

from ta_core.domain.entities.verify import HostVerification as HostVerificationEntity
from ta_core.infrastructure.sqlalchemy.models.commons.verify import HostVerification
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository
from ta_core.utils.uuid import UUID


class HostVerificationRepository(
    AbstractRepository[HostVerificationEntity, HostVerification]
):
    @property
    def _model(self) -> type[HostVerification]:
        return HostVerification

    async def create_host_verification_async(
        self,
        entity_id: UUID,
        host_email: EmailStr,
        verification_token: UUID,
        token_expires_at: datetime,
    ) -> HostVerificationEntity | None:
        host_verification = HostVerificationEntity(
            entity_id=entity_id,
            host_email=host_email,
            verification_token=verification_token,
            token_expires_at=token_expires_at,
        )
        return await self.create_async(host_verification)

    async def read_latest_by_host_email_or_none_async(
        self, host_email: EmailStr
    ) -> HostVerificationEntity | None:
        host_verifications = await self.read_order_by_limit_async(
            where=(self._model.host_email == host_email,),
            order_by=self._model.token_expires_at.desc(),
            limit=1,
        )
        return host_verifications[0] if host_verifications else None
