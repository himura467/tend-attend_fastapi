from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class CreateAccountRequest(BaseModel):
    login_id: str = Field(..., title="Login ID")
    login_password: str = Field(..., title="Login Password")


@router.post("/account", name="Create Account", response_model=None)
async def create_account(request: CreateAccountRequest) -> None:
    pass
