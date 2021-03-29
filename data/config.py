from typing import Final

from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = [int(el) for el in env.list("ADMINS")]  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста

DB_USER: Final[str] = env.str('POSTGRES_USER')
DB_PASS: Final[str] = env.str('POSTGRES_PASSWORD')
DB_HOST: Final[str] = env.str('POSTGRES_HOST')
DB_NAME: Final[str] = env.str('POSTGRES_DB')

NUMBER_PATTERN: Final[str] = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
