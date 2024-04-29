from fastapi import APIRouter
from ta_core.dtos.auth import CreateAccountRequest, CreateAccountResponse

router = APIRouter()


@router.post("/account", name="Create Account", response_model=CreateAccountResponse)
async def create_account(request: CreateAccountRequest) -> CreateAccountResponse:
    pass
