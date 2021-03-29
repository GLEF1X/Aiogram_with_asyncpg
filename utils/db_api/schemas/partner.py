from typing import Optional, List, Union
from asyncpg import Record

from utils.db_api.postgresql import BaseDB


class Partner(BaseDB):

    async def create_table(self) -> None:
        sql = f"""CREATE TABLE IF NOT EXISTS {self.db_name}(
            partner_id int GENERATED ALWAYS AS IDENTITY NOT NULL,
            partner_service VARCHAR(200) NOT NULL,
            company_name varchar(100) NOT NULL,
            contact_name varchar(120) NOT NULL,
            instagram_link varchar(200) NULL,
            whatsapp_link varchar(150) NULL,
            contact_number varchar(200) NOT NULL,
            comment text NULL,
            CONSTRAINT PK_{self.db_name}_partner_id PRIMARY KEY (partner_id));
            -- создаем индексы для таблицы
            CREATE INDEX IF NOT EXISTS {self.db_name}_contact_number_index ON {self.db_name} USING HASH(contact_number);
            CREATE INDEX IF NOT EXISTS {self.db_name}_company_name_index ON {self.db_name} USING HASH(company_name);
            CREATE INDEX IF NOT EXISTS {self.db_name}_contact_name_index ON {self.db_name}(contact_name);
        """
        await self.execute(sql, execute=True)

    async def add_entry(self, company_name: str, contact_name: str,
                        partner_service: str,
                        contact_number: str, comment: Optional[str],
                        instagram_link: Optional[str] = None, whatsapp_link: Optional[str] = None) -> str:
        sql = f"""INSERT INTO {self.db_name}(
            company_name, contact_name, instagram_link, partner_service, whatsapp_link, contact_number, comment
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)"""
        return await self.execute(
            sql, company_name, contact_name, instagram_link, partner_service, whatsapp_link,
            contact_number,
            comment, execute=True
        )

    async def add_defaults(self):
        await self.add_entry(
            company_name='Артур/ контейнера',
            partner_service='ГРУЗОПЕРЕВОЗКИ И РАЗНОРАБОЧИЕ',
            comment="""Цена контейнера 4500руб, продавать нужно за
5.000руб
Партнерская комиссия: 500р""",
            contact_name='Артур',
            contact_number='8(917)234-14-43'
        )
        await self.add_entry(
            company_name='Газель',
            partner_service='ГРУЗОПЕРЕВОЗКИ И РАЗНОРАБОЧИЕ',
            contact_name='Сергей',
            contact_number='8(917)906-47-70',
            comment="""Вывоз мусора, Газель
В зависимости от объема мусора 2000-2500руб
Грузчики 350р/час (минимум час)
Партнерские комиссионные то что сверху"""
        )

    async def setup(self, add_defaults: bool = False) -> None:
        await self.create()
        await self.create_table()
        if add_defaults:
            await self.add_defaults()

    async def select_services(self) -> Union[Optional[List[Record]], list]:
        sql = f"""SELECT DISTINCT partner_service FROM {self.db_name}"""
        return await self.execute(sql, fetch=True)
