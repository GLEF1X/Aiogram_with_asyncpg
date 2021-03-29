from typing import Literal, Optional, Any, List

import asyncpg
from loguru import logger

from utils.db_api.postgresql import BaseDB, FormatType


class Employee(BaseDB):
    """Класс бд работника"""

    async def create_table(self) -> None:
        sql = f"""
        CREATE TYPE employee_type AS ENUM
            ('Плиточник', 'Маляр');

        CREATE TABLE IF NOT EXISTS {self.db_name}(
        employee_id int GENERATED ALWAYS AS IDENTITY NOT NULL,
        type employee_type NOT NULL,
        name varchar(255) NOT NULL,   
        phone_number varchar(50) NOT NULL,
        comment TEXT NULL DEFAULT '-',
        type_of_employment varchar(255) NOT NULL DEFAULT '-',
        photo_id BIGINT,
        CONSTRAINT PK_{self.db_name}_employee_id PRIMARY KEY (employee_id));
        
        CREATE INDEX IF NOT EXISTS {self.db_name}_type_index ON {self.db_name} USING HASH(type);
        CREATE INDEX IF NOT EXISTS {self.db_name}_employee_id ON {self.db_name}(employee_id);
        """
        try:
            await self.execute(sql, execute=True)
            logger.info(f'Успешно создана таблица {self.db_name}')
        except asyncpg.DuplicateObjectError:
            pass

    async def add_entry(self, employee_type: Literal['Плиточник', 'Маляр'], name: str,
                        phone_number: str,
                        type_of_employment: Literal['Занят', 'Не занят'],
                        photo_id: Optional[int] = None,
                        comment: Optional[str] = None) -> Any:
        sql = f"""INSERT INTO {self.db_name}(type, name, phone_number, comment, photo_id, type_of_employment)
        VALUES($1, $2, $3, $4, $5, $6) RETURNING *"""
        return await self.execute(
            sql, employee_type, name, phone_number, comment, photo_id, type_of_employment, fetchrow=True
        )

    async def select_entry(self, or_format: bool = False, **kwargs: Any) -> Optional[List[asyncpg.Record]]:
        sql = f"""SELECT * FROM {self.db_name} WHERE """
        sql, parameters = self.format_arguments(sql, kwargs,
                                                format_type=FormatType.OR_ if or_format else FormatType.AND_)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_master_by_phone(self, phone_number: str, default_number: str) -> asyncpg.Record:
        sql = f"""SELECT * FROM {self.db_name}
         WHERE phone_number = $1 
         OR phone_number = $2 OR phone_number = $3"""
        return await self.execute(sql, "+" + phone_number, default_number, phone_number,
                                  fetchrow=True)

    async def add_defaults(self) -> None:
        await self.add_entry(
            employee_type='Плиточник',
            phone_number='+7(903)343-81-78',
            photo_id=45234453,
            name='Рамис'
        )
        await self.add_entry(
            employee_type='Маляр',
            phone_number='+7(965)692-69-82',
            photo_id=54456456,
            name='Радик'
        )

    @logger.catch
    async def setup(self, add_defaults: bool = False) -> None:
        await self.create()
        await self.create_table()
        if add_defaults:
            try:
                await self.add_defaults()
            except asyncpg.UniqueViolationError as ex:
                logger.error(ex)
            except asyncpg.UndefinedTableError as ex:
                logger.error(ex)

    async def select_types(self) -> Optional[List[asyncpg.Record]]:
        sql = f"""SELECT DISTINCT type FROM {self.db_name}"""
        return await self.execute(sql, fetch=True)

    async def get_by_type(self, master_type: Literal['Плиточник', 'Маляр']) -> Optional[List[asyncpg.Record]]:
        if master_type == 'Плиточники':
            master_type = 'Плиточник'
        master_type = master_type.replace("ы", "")
        sql = F"""SELECT * FROM {self.db_name} WHERE """
        sql, parameters = self.format_arguments(sql, parameters={
            'type': master_type
        })
        return await self.execute(sql, *parameters, fetch=True)
