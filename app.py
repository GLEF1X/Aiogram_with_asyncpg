from aiogram import executor, Dispatcher
from loguru import logger

from loader import manager


@logger.catch
async def on_startup(dispatcher: Dispatcher):
    # Уведомляет про запуск
    # await on_startup_notify(dispatcher)
    # Создаем таблицы в бд
    await manager.setup()
    logger.info("Bot started")

if __name__ == '__main__':
    from handlers import dp

    logger.info('Starting bot')
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
