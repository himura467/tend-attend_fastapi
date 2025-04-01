from alembic import command
from fastapi import APIRouter
from ta_core.dtos.admin_dto.migration import (
    StampRevisionRequest,
    StampRevisionResponse,
    UpgradeDbResponse,
)
from ta_core.utils.alembic import get_alembic_config

router = APIRouter()


# TODO: JWT で認証されたユーザーのみがこのエンドポイントを呼び出せるようにする
@router.post(
    path="/stamp",
    name="Stamp Revision",
    response_model=StampRevisionResponse,
)
def stamp_revision(req: StampRevisionRequest) -> StampRevisionResponse:
    revision = req.revision

    alembic_config = get_alembic_config()
    command.stamp(alembic_config, revision)

    return StampRevisionResponse(error_codes=())


# TODO: JWT で認証されたユーザーのみがこのエンドポイントを呼び出せるようにする
@router.post(
    path="/upgrade",
    name="Upgrade DB",
    response_model=UpgradeDbResponse,
)
def upgrade_db() -> UpgradeDbResponse:
    alembic_config = get_alembic_config()
    command.upgrade(alembic_config, "head")

    return UpgradeDbResponse(error_codes=())
