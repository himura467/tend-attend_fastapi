from datetime import datetime

from pydantic.networks import EmailStr

from ta_core.domain.entities.verify import HostVerification as HostVerificationEntity
from ta_core.infrastructure.sqlalchemy.models.shards.verify import HostVerification
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository


class HostVerificationRepository(
    AbstractRepository[HostVerificationEntity, HostVerification]
):
    async def create_host_verification_async(
        self,
        entity_id: str,
        host_email: EmailStr,
        verification_token: str,
        token_expires_at: datetime,
    ) -> HostVerificationEntity | None:
        host_verification = HostVerificationEntity(
            entity_id=entity_id,
            host_email=host_email,
            verification_token=verification_token,
            token_expires_at=token_expires_at,
        )
        return await self.create_async(host_verification)
