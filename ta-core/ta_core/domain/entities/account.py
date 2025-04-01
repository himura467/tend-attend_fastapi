from datetime import datetime

from pydantic.networks import EmailStr

from ta_core.domain.entities.base import IEntity
from ta_core.features.account import Gender
from ta_core.utils.uuid import UUID


class UserAccount(IEntity):
    def __init__(
        self,
        entity_id: UUID,
        user_id: int,
        username: str,
        hashed_password: str,
        refresh_token: str | None,
        nickname: str | None,
        birth_date: datetime,
        gender: Gender,
        email: EmailStr,
        email_verified: bool,
        followee_ids: list[UUID],
        followees: list["UserAccount"],
        follower_ids: list[UUID],
        followers: list["UserAccount"],
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.username = username
        self.hashed_password = hashed_password
        self.refresh_token = refresh_token
        self.nickname = nickname
        self.birth_date = birth_date
        self.gender = gender
        self.email = email
        self.email_verified = email_verified
        self.followee_ids = followee_ids
        self.followees = followees
        self.follower_ids = follower_ids
        self.followers = followers

    def set_refresh_token(self, refresh_token: str) -> "UserAccount":
        return UserAccount(
            entity_id=self.id,
            user_id=self.user_id,
            username=self.username,
            hashed_password=self.hashed_password,
            refresh_token=refresh_token,
            nickname=self.nickname,
            birth_date=self.birth_date,
            gender=self.gender,
            email=self.email,
            email_verified=self.email_verified,
            followee_ids=self.followee_ids,
            followees=self.followees,
            follower_ids=self.follower_ids,
            followers=self.followers,
        )
