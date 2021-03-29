from aiogram import types

from loader import manager


async def check_promo(message: types.Message) -> bool:
    promo = await manager.promo_code.select_entry(
        promo_value=message.text
    )
    if promo:
        await manager.user.add_entry(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        await manager.promo_code.delete_entry(
            promo_value=message.text
        )
        return True
    return False


async def get_all_masters():
    return await manager.employee.select_all()


async def get_master_types():
    return await manager.employee.select_types()


async def get_masters_by_type(master_type: str):
    return await manager.employee.get_by_type(master_type)
