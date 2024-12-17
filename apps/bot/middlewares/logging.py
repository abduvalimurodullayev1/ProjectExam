from aiogram.types import Update, User
from aiogram import BaseMiddleware

from typing import Callable, Dict, Any, Awaitable

EVENT_FROM_USER = 'event_from_user'

from loguru import logger


class LoggingMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        user: User = data.get(EVENT_FROM_USER)

        # logger.info(f"Receive update {event}")
        logger.info(f"User: {user}")
        return await handler(event, data)


__all__ = [
    'LoggingMiddleware'
]
