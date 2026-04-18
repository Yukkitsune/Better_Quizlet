import sqlite3
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Any, Callable, Awaitable, Dict


class DBMiddleware(BaseMiddleware):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        data["db_conn"] = self.conn
        return await handler(event, data)
