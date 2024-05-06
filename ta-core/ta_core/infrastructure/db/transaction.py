from functools import wraps
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar, cast

from ta_core.dtos.base import BaseModelWithErrorCodes

P = ParamSpec("P")
UseCaseMethodType = Callable[P, Coroutine[Any, Any, BaseModelWithErrorCodes]]
TUseCaseMethod = TypeVar("TUseCaseMethod", bound=UseCaseMethodType)  # type: ignore


def rollbackable(f: TUseCaseMethod) -> TUseCaseMethod:
    @wraps(f)
    async def wrapper(
        self: Any, *args: P.args, **kwargs: P.kwargs
    ) -> BaseModelWithErrorCodes:
        response: BaseModelWithErrorCodes = await f(self, *args, **kwargs)
        if response.error_codes:
            await self.unit_of_work.rollback_async()
        else:
            await self.unit_of_work.commit_async()
        return response

    return cast(TUseCaseMethod, wrapper)
