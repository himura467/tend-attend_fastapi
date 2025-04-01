from datetime import datetime

from pydantic.networks import EmailStr

from ta_core.domain.entities.base import IEntity
from ta_core.utils.uuid import UUID


class EmailVerification(IEntity):
    def __init__(
        self,
        entity_id: UUID,
        email: EmailStr,
        verification_token: UUID,
        token_expires_at: datetime,
    ) -> None:
        super().__init__(entity_id)
        self.email = email
        self.verification_token = verification_token
        self.token_expires_at = token_expires_at
