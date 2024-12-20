from pydantic.networks import EmailStr

from ta_core.domain.entities.base import IEntity
from ta_core.features.account import Gender


class HostAccount(IEntity):
    def __init__(
        self,
        entity_id: str,
        host_name: str,
        hashed_password: str,
        refresh_token: str | None,
        email: EmailStr,
        user_id: int | None,
        guests: list["GuestAccount"] | None = None,
    ) -> None:
        super().__init__(entity_id)
        self.host_name = host_name
        self.hashed_password = hashed_password
        self.refresh_token = refresh_token
        self.email = email
        self.user_id = user_id
        self.guests = guests

    def set_refresh_token(self, refresh_token: str) -> "HostAccount":
        return HostAccount(
            entity_id=self.id,
            host_name=self.host_name,
            hashed_password=self.hashed_password,
            refresh_token=refresh_token,
            email=self.email,
            user_id=self.user_id,
            guests=self.guests,
        )


class GuestAccount(IEntity):
    def __init__(
        self,
        entity_id: str,
        guest_first_name: str,
        guest_last_name: str,
        guest_nickname: str | None,
        age: int,
        gender: Gender,
        hashed_password: str,
        refresh_token: str | None,
        user_id: int,
        host_id: str,
    ) -> None:
        super().__init__(entity_id)
        self.guest_first_name = guest_first_name
        self.guest_last_name = guest_last_name
        self.guest_nickname = guest_nickname
        self.age = age
        self.gender = gender
        self.hashed_password = hashed_password
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.host_id = host_id

    def set_refresh_token(self, refresh_token: str) -> "GuestAccount":
        return GuestAccount(
            entity_id=self.id,
            guest_first_name=self.guest_first_name,
            guest_last_name=self.guest_last_name,
            guest_nickname=self.guest_nickname,
            age=self.age,
            gender=self.gender,
            hashed_password=self.hashed_password,
            refresh_token=refresh_token,
            user_id=self.user_id,
            host_id=self.host_id,
        )
