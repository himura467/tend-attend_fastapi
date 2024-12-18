from fastapi import APIRouter
from ta_core.dtos.admin import MigrateAuroraResponse
from ta_core.infrastructure.sqlalchemy.migrate_db import setup_aurora

router = APIRouter()


# TODO: JWT で認証されたユーザーのみがこのエンドポイントを呼び出せるようにする
@router.post(
    path="/migrate/aurora",
    name="Migrate Aurora",
    response_model=MigrateAuroraResponse,
)
async def migrate_aurora() -> MigrateAuroraResponse:
    setup_aurora()
    return MigrateAuroraResponse()
