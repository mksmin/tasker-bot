from abc import ABC, abstractmethod
from typing import Any


class BaseHandler(ABC):
    @abstractmethod
    async def handle(
        self,
        payload: dict[str, Any],
    ) -> Any: ...
