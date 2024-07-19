from ta_core.domain.entities.base import IEntity
from ta_core.features.account import Group


class Account(IEntity):
    def __init__(
        self,
        entity_id: str,
        email: str,
        hashed_password: str,
        refresh_token: str | None,
        group: Group,
    ) -> None:
        super().__init__(entity_id)
        self.email = email
        self.hashed_password = hashed_password
        self.refresh_token = refresh_token
        self.group = group

    def set_refresh_token(self, refresh_token: str) -> "Account":
        return Account(
            entity_id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            refresh_token=refresh_token,
            group=self.group,
        )


class HostAccount(IEntity):
    def __init__(
        self, entity_id: str, account_id: str, user_id: int | None, host_name: str
    ) -> None:
        super().__init__(entity_id)
        self.account_id = account_id
        self.user_id = user_id
        self.host_name = host_name


class GuestAccount(IEntity):
    def __init__(
        self,
        entity_id: str,
        account_id: str,
        user_id: int | None,
        host_id: str,
        guest_name: str,
    ) -> None:
        super().__init__(entity_id)
        self.account_id = account_id
        self.user_id = user_id
        self.host_id = host_id
        self.guest_name = guest_name
