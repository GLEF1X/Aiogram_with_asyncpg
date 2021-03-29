import logging
from typing import Optional, Union

from utils.db_api.postgresql import BaseDB


class User(BaseDB):

    async def select_entry(self, **kwargs):
        sql = f"SELECT * FROM {self.db_name} WHERE "
        sql, parameters = self.format_arguments(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def add_entry(self, full_name: str, username: Optional[str], telegram_id: Union[str, int]):
        sql = f"INSERT INTO {self.db_name}(full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def create_table(self):
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.db_name} (
        user_id int GENERATED ALWAYS AS IDENTITY NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        CONSTRAINT PK_{self.db_name}_user_id PRIMARY KEY (user_id));
        
        CREATE INDEX IF NOT EXISTS {self.db_name}_telegram_id_index ON {self.db_name} USING HASH(telegram_id);
        ;
        """
        await self.execute(sql, execute=True)
        logging.info(f'Успешно создана таблица {self.db_name}')

    async def count_users(self):
        sql = f"SELECT COUNT(*) FROM {self.db_name}"
        return await self.execute(sql, fetchval=True)
