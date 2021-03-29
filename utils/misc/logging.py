import sys
from functools import wraps
from typing import Callable, TypeVar, Any

from loguru import logger

logger.add(sys.stdout, format="{time} <red>{level}</red> {message}", filter="my_module", level="INFO", diagnose=True,
           backtrace=True,
           colorize=True)

F = TypeVar('F', bound=Callable[..., Any])


def create_log(func: F, table_name: str):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await func(*args, **kwargs)
        logger.info(f"Успешно создана таблица {table_name}")

    return wrapper
