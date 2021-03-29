import asyncpg
from loguru import logger

from utils.db_api.postgresql import BaseDB


class PromoCode(BaseDB):

    async def create_table(self):
        sql = f"""CREATE TABLE IF NOT EXISTS {self.db_name}(
            promo_id int GENERATED ALWAYS AS IDENTITY NOT NULL,
            promo_value varchar(200) NOT NULL UNIQUE DEFAULT md5(random()::text),
            CONSTRAINT PK_{self.db_name}_promo_id PRIMARY KEY (promo_id));
            
            CREATE INDEX IF NOT EXISTS {self.db_name}_promo_code_value_index ON {self.db_name} USING HASH(promo_value);
        """
        await self.execute(sql, execute=True)
        logger.info(f'Успешно создана таблица {self.db_name}')

    async def add_entry(self, *args, **kwargs):
        try:
            sql = f"""INSERT INTO {self.db_name} DEFAULT VALUES RETURNING *"""
            return await self.execute(
                sql, fetchrow=True
            )
        except asyncpg.UniqueViolationError:
            logger.info(
                "Такой промокод уже есть в базе данных, table name: {table_name}".format(table_name=self.db_name)
            )

    async def generate_some_promo(self, count: int = 10):
        for _ in range(count):
            await self.add_entry()

    async def setup(self, add_defaults: bool = False) -> None:
        await self.create()
        await self.create_table()
        if add_defaults:
            await self.generate_some_promo()
