from ta_core.domain.entities.base import IEntity


class Account(IEntity):
    def __init__(
        self,
        entity_id: str,
        login_id: str,
        login_password: str,
        refresh_token: str | None,
        user_id: int | None,
    ) -> None:
        super().__init__(entity_id)
        self.login_id = login_id
        self.login_password = login_password
        self.refresh_token = refresh_token
        self.user_id = user_id

    @staticmethod
    def default(
        entity_id: str,
        login_id: str,
        login_password: str,
    ) -> "Account":
        return Account(
            entity_id=entity_id,
            login_id=login_id,
            login_password=login_password,
            refresh_token=None,
            user_id=None,
        )
