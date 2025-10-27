import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])


def coro(f: F) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(f(*args, **kwargs))

    return wrapper
