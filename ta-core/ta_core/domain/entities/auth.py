from ta_core.domain.entities.base import IEntity
from ta_core.features.auth import Group


class Account(IEntity):
    def __init__(
        self,
        entity_id: str,
        login_id: str,
        login_password_hashed: str,
        refresh_token: str | None,
        user_id: int | None,
        group: Group,
    ) -> None:
        super().__init__(entity_id)
        self.login_id = login_id
        self.login_password_hashed = login_password_hashed
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.group = group

    @staticmethod
    def default(
        entity_id: str,
        login_id: str,
        login_password_hashed: str,
        group: Group,
    ) -> "Account":
        return Account(
            entity_id=entity_id,
            login_id=login_id,
            login_password_hashed=login_password_hashed,
            refresh_token=None,
            user_id=None,
            group=group,
        )

    def set_refresh_token(self, refresh_token: str) -> "Account":
        return Account(
            entity_id=self.id,
            login_id=self.login_id,
            login_password_hashed=self.login_password_hashed,
            refresh_token=refresh_token,
            user_id=self.user_id,
            group=self.group,
        )
