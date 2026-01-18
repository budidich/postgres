Здесь находится разговор между пользователем Рома и консультантом по линуксу Deepseek

# Рома:
У меня компьютер на windows, на нем установлены Docker и WSL2.
Для того, чтобы в будущем работать с 1С я скачал с сайта 1С дистрибутив postgres 
postgresql_17.6_1_ubuntu_24.04_x86_64_package.tar.bz2
Я хочу создать контейнер docker и в нем установить скачанный мной postgres 
Желательно сделать это не вручную командами, а настройкой конфигурационного файла yaml
как это сделать?


# Deepseek:
Для создания контейнера Docker с вашим скачанным дистрибутивом PostgreSQL для 1С, лучше всего создать docker-compose.yml файл и Dockerfile. Вот пошаговое решение:

1. Структура проекта
Создайте следующую структуру папок:

text
project/
├── docker-compose.yml
├── Dockerfile
├── postgresql_17.6_1_ubuntu_24.04_x86_64_package.tar.bz2
└── init-scripts/
    └── init.sql (опционально)
2. Dockerfile
Создайте Dockerfile для установки вашего PostgreSQL:

dockerfile
FROM ubuntu:24.04

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    sudo \
    libreadline8 \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем русскую локаль для корректной работы с 1С
RUN locale-gen ru_RU.UTF-8 && locale-gen en_US.UTF-8
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

# Создаем директорию для установки
WORKDIR /tmp

# Копируем скачанный архив PostgreSQL
COPY postgresql_17.6_1_ubuntu_24.04_x86_64_package.tar.bz2 /tmp/

# Распаковываем и устанавливаем PostgreSQL
RUN tar -xjf postgresql_17.6_1_ubuntu_24.04_x86_64_package.tar.bz2 && \
    cd postgresql_17.6_1_ubuntu_24.04_x86_64_package && \
    ./install.sh

# Создаем пользователя и директории для данных
RUN useradd -r -s /bin/bash postgres && \
    mkdir -p /var/lib/postgresql/data && \
    chown -R postgres:postgres /var/lib/postgresql && \
    mkdir -p /docker-entrypoint-initdb.d

# Копируем скрипт инициализации
COPY init-scripts/ /docker-entrypoint-initdb.d/

# Настраиваем переменные окружения
ENV PGDATA /var/lib/postgresql/data
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB postgres

# Экспортируем порт
EXPOSE 5432

# Переключаемся на пользователя postgres
USER postgres

# Инициализируем БД и запускаем PostgreSQL
RUN /opt/1C/v8.3/x86_64/pgpro/bin/initdb -D $PGDATA --locale=ru_RU.UTF-8

# Копируем конфигурационные файлы
COPY --chown=postgres:postgres postgresql.conf /var/lib/postgresql/data/
COPY --chown=postgres:postgres pg_hba.conf /var/lib/postgresql/data/

# Запускаем PostgreSQL
CMD ["/opt/1C/v8.3/x86_64/pgpro/bin/postgres", "-D", "/var/lib/postgresql/data"]
3. docker-compose.yml
Создайте основной конфигурационный файл:

yaml
version: '3.8'

services:
  postgres-1c:
    build: .
    container_name: postgres-1c
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_secure_password_here
      POSTGRES_DB: postgres
      PGDATA: /var/lib/postgresql/data
      LC_ALL: ru_RU.UTF-8
      LANG: ru_RU.UTF-8
    volumes:
      # Для сохранения данных
      - postgres_data:/var/lib/postgresql/data
      # Для кастомных конфигов (опционально)
      - ./postgresql.conf:/var/lib/postgresql/data/postgresql.conf:ro
      - ./pg_hba.conf:/var/lib/postgresql/data/pg_hba.conf:ro
      # Для инициализационных скриптов
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    networks:
      - 1c-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    name: postgres-1c-data

networks:
  1c-network:
    driver: bridge
4. Конфигурационные файлы PostgreSQL (опционально)
Создайте базовые конфигурационные файлы:

postgresql.conf:

conf
listen_addresses = '*'
port = 5432
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix
pg_hba.conf:

conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             0.0.0.0/0               md5
5. Скрипт инициализации (опционально)
Создайте init-scripts/init.sql:

sql
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
6. Запуск контейнера
Поместите скачанный архив postgresql_17.6_1_ubuntu_24.04_x86_64_package.tar.bz2 в папку с проектом

Откройте терминал в директории проекта

Выполните команду:

bash
docker-compose up -d --build
7. Проверка работы
bash
# Проверить статус контейнера
docker-compose ps

# Посмотреть логи
docker-compose logs -f postgres-1c

# Подключиться к базе данных
docker exec -it postgres-1c psql -U postgres
Важные замечания:
Пароль: Измените your_secure_password_here в docker-compose.yml на безопасный пароль

WSL2: Убедитесь, что Docker Desktop использует WSL2 backend

Лицензия: Убедитесь, что у вас есть лицензия на использование PostgreSQL от 1С

Производительность: Для production используйте настройки shared_buffers и других параметров в соответствии с ресурсами вашего сервера

Это решение обеспечит вам готовый к работе контейнер PostgreSQL для 1С с возможностью простого управления через Docker Compose.