from datetime import datetime

from pydantic.networks import EmailStr

from ta_core.domain.entities.base import IEntity
from ta_core.utils.uuid import UUID


class HostVerification(IEntity):
    def __init__(
        self,
        entity_id: UUID,
        host_email: EmailStr,
        verification_token: UUID,
        token_expires_at: datetime,
    ) -> None:
        super().__init__(entity_id)
        self.host_email = host_email
        self.verification_token = verification_token
        self.token_expires_at = token_expires_at
