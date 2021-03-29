from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import ADMINS
from loader import manager


class IsRegistered(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        if await manager.user.select_entry(telegram_id=message.from_user.id):
            return True
        return False


class IsNotRegistered(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        if not await manager.user.select_entry(telegram_id=message.from_user.id):
            return True
        return False


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.from_user.id in ADMINS
