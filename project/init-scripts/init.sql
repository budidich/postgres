-- Создание базы данных для 1С
CREATE DATABASE "1C_DB" 
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'ru_RU.UTF-8'
    LC_CTYPE = 'ru_RU.UTF-8'
    CONNECTION LIMIT = -1;

-- Настройка параметров для 1С (рекомендуемые)
ALTER DATABASE "1C_DB" SET default_transaction_isolation = 'read committed';
ALTER DATABASE "1C_DB" SET lock_timeout = '3s';