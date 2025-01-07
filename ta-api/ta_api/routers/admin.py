from fastapi import APIRouter
from ta_core.dtos.admin import ResetAuroraResponse
from ta_core.infrastructure.sqlalchemy.migrate_db import reset_aurora_db

from ta_api.routers.admin_router import migration

router = APIRouter()

router.include_router(
    migration.router,
    prefix="/migration",
    tags=["migration"],
)


# TODO: JWT で認証されたユーザーのみがこのエンドポイントを呼び出せるようにする
@router.post(
    path="/reset/aurora",
    name="Reset Aurora DB",
    response_model=ResetAuroraResponse,
)
def reset_aurora() -> ResetAuroraResponse:
    reset_aurora_db()
    return ResetAuroraResponse(error_codes=())
