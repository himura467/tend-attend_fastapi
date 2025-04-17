import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ta_ml.constants import timesfm

from ta_core.domain.entities.event import (
    EventAttendanceActionLog as EventAttendanceActionLogEntity,
)
from ta_core.dtos.base import BaseModelWithErrorCodes
from ta_core.features.account import Gender
from ta_core.features.event import AttendanceAction, Frequency, Weekday
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.repositories.account import UserAccountRepository
from ta_core.infrastructure.sqlalchemy.repositories.event import (
    EventAttendanceActionLogRepository,
    EventRepository,
    RecurrenceRepository,
    RecurrenceRuleRepository,
)
from ta_core.use_case.unit_of_work_base import IUnitOfWork
from ta_core.utils.uuid import generate_uuid


@dataclass(frozen=True)
class DevelopUseCase:
    uow: IUnitOfWork

    @rollbackable
    async def mock_user_attendance_sequence_async(self) -> BaseModelWithErrorCodes:
        user_account_repository = UserAccountRepository(self.uow)
        recurrence_rule_repository = RecurrenceRuleRepository(self.uow)
        recurrence_repository = RecurrenceRepository(self.uow)
        event_repository = EventRepository(self.uow)
        event_attendance_action_log_repository = EventAttendanceActionLogRepository(
            self.uow
        )

        host = await user_account_repository.create_user_account_async(
            entity_id=generate_uuid(),
            user_id=0,
            username="host",
            hashed_password="hashed_password",
            birth_date=datetime(year=1970, month=1, day=1, tzinfo=ZoneInfo("UTC")),
            gender=Gender.MALE,
            email="email@example.com",
            followee_ids=set(),
            follower_ids=set(),
        )
        assert host is not None

        recurrence_rule_id = generate_uuid()
        recurrence_rule = await recurrence_rule_repository.create_recurrence_rule_async(
            entity_id=recurrence_rule_id,
            user_id=0,
            freq=Frequency.DAILY,
            until=None,
            count=None,
            interval=1,
            bysecond=None,
            byminute=None,
            byhour=None,
            byday=None,
            bymonthday=None,
            byyearday=None,
            byweekno=None,
            bymonth=None,
            bysetpos=None,
            wkst=Weekday.MO,
        )
        assert recurrence_rule is not None

        recurrence_id = generate_uuid()
        await recurrence_repository.create_recurrence_async(
            entity_id=recurrence_id,
            user_id=0,
            rrule_id=recurrence_rule_id,
            rrule=recurrence_rule,
            rdate=[],
            exdate=[],
        )

        event_id = generate_uuid()
        await event_repository.create_event_async(
            entity_id=event_id,
            user_id=0,
            summary="summary",
            location=None,
            start=datetime(year=2000, month=1, day=1, tzinfo=ZoneInfo("UTC")),
            end=datetime(year=2000, month=1, day=2, tzinfo=ZoneInfo("UTC")),
            is_all_day=True,
            recurrence_id=recurrence_id,
            timezone="UTC",
        )

        # Users depending on the potential weekly event
        user_ids = range(1, 11)

        today = datetime.now(ZoneInfo("UTC")).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=ZoneInfo("UTC")
        )

        for user_id in user_ids:
            await user_account_repository.create_user_account_async(
                entity_id=generate_uuid(),
                user_id=user_id,
                username=f"username{user_id}",
                hashed_password="hashed_password",
                birth_date=datetime(year=1970, month=1, day=1, tzinfo=ZoneInfo("UTC")),
                gender=Gender.MALE,
                email=f"email{user_id}@example.com",
                followee_ids={host.id},
                follower_ids=set(),
            )

            for i in range(timesfm.CONTEXT_LEN):
                start = today - timedelta(days=i)
                attend_log = EventAttendanceActionLogEntity(
                    entity_id=generate_uuid(),
                    user_id=user_id,
                    event_id=event_id,
                    start=start,
                    action=AttendanceAction.ATTEND,
                    acted_at=(
                        start + timedelta(hours=random.uniform(5, 7))
                        if start.weekday() != 5 and start.weekday() != 6
                        else start + timedelta(hours=random.uniform(11, 13))
                    ),
                )
                leave_log = EventAttendanceActionLogEntity(
                    entity_id=generate_uuid(),
                    user_id=user_id,
                    event_id=event_id,
                    start=start,
                    action=AttendanceAction.LEAVE,
                    acted_at=(start + timedelta(hours=random.uniform(17, 19))),
                )
                await event_attendance_action_log_repository.bulk_create_event_attendance_action_logs_async(
                    [attend_log, leave_log]
                )

        return BaseModelWithErrorCodes(error_codes=())
