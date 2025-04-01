from functools import wraps
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar, cast

from ta_core.dtos.base import BaseModelWithErrorCodes

P = ParamSpec("P")
UseCaseMethodType = Callable[P, Coroutine[Any, Any, BaseModelWithErrorCodes]]
TUseCaseMethod = TypeVar("TUseCaseMethod", bound=UseCaseMethodType)  # type: ignore[type-arg]


def rollbackable(f: TUseCaseMethod) -> TUseCaseMethod:
    @wraps(f)
    async def wrapper(
        self: Any, *args: P.args, **kwargs: P.kwargs  # type: ignore[valid-type]
    ) -> BaseModelWithErrorCodes:
        response: BaseModelWithErrorCodes = await f(self, *args, **kwargs)
        if response.error_codes:
            await self.uow.rollback_async()
        else:
            await self.uow.commit_async()
        return response

    return cast(TUseCaseMethod, wrapper)
