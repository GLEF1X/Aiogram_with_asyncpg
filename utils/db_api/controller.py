import asyncio

from loguru import logger

from utils.db_api.schemas.employee import Employee
from utils.db_api.schemas.partner import Partner
from utils.db_api.schemas.promo_code import PromoCode
from utils.db_api.schemas.user import User


class Manager:
    """Менеджер для управления всеми моделями сразу"""

    def __init__(self) -> None:
        self.user = User()
        self.partner = Partner()
        self.promo_code = PromoCode()
        self.employee = Employee()

    async def setup(self) -> None:
        logger.info("Configuring database")
        await asyncio.gather(
            self.user.setup(),
            self.employee.setup(),
            self.promo_code.setup(),
            self.partner.setup()
        )
        logger.info("Database was configured")
