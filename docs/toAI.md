# Анализ проекта


**Текущий каталог:** `/mnt/d/dev/postgres`


## Структура проекта

```
📁 init-scripts/
⚙️ docker-compose.yml
📄 dockerfile
📄 pg_hba.conf
📄 postgresql.conf
  📄 init.sql
```

*Примечание: пропущено 4 игнорируемых элементов (архивы, бинарные файлы, служебные каталоги)*

---


## Содержимое файлов



============================================================

### Файл: `docker-compose.yml`


```yml

services:
  postgres-1c:
    build: .
    container_name: postgres-1c
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgrespassword
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


```



============================================================

### Файл: `dockerfile`


```text

FROM ubuntu:24.04

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    sudo \
    libreadline8 \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем русскую локаль
RUN locale-gen ru_RU.UTF-8 && locale-gen en_US.UTF-8
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

# Создаем пользователя
RUN useradd -r -s /bin/bash postgres

# Копируем и устанавливаем PostgreSQL из .deb пакетов
WORKDIR /tmp
COPY postgresql_17.6_1_ubuntu_24.04_x86_64_package.tar.bz2 /tmp/

# Распаковываем архив
RUN tar -xjf postgresql_17.6_1_ubuntu_24.04_x86_64_package.tar.bz2 && \
    ls -la && \
    echo "Устанавливаем .deb пакеты..." && \
    # Устанавливаем пакеты в правильном порядке
    dpkg -i postgresql-common_*.deb || true && \
    dpkg -i libpq5_*.deb || true && \
    dpkg -i libecpg6_*.deb || true && \
    dpkg -i libpgtypes3_*.deb || true && \
    dpkg -i libecpg-compat3_*.deb || true && \
    dpkg -i postgresql-client-common_*.deb || true && \
    dpkg -i postgresql-client-17_*.deb || true && \
    dpkg -i postgresql-17_*.deb || true && \
    # Исправляем зависимости
    apt-get update && apt-get -f install -y && \
    rm -rf /var/lib/apt/lists/*

# Создаем необходимые директории
RUN mkdir -p /var/lib/postgresql/data && \
    chown -R postgres:postgres /var/lib/postgresql && \
    mkdir -p /docker-entrypoint-initdb.d

# Копируем скрипт инициализации
COPY init-scripts/ /docker-entrypoint-initdb.d/

# Переменные окружения
ENV PGDATA /var/lib/postgresql/data
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB postgres

# Открываем порт
EXPOSE 5432

# Рабочий каталог и пользователь
WORKDIR /var/lib/postgresql
USER postgres

# Скрипт запуска
#COPY --chown=postgres:postgres docker-entrypoint.sh /usr/local/bin/
#RUN chmod +x /usr/local/bin/docker-entrypoint.sh

#ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
#CMD ["/opt/1C/postgres/17.6-1/bin/postgres", "-D", "/var/lib/postgresql/data"]


```



============================================================

### Файл: `pg_hba.conf`


```conf

# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             0.0.0.0/0               md5


```



============================================================

### Файл: `postgresql.conf`


```conf

listen_addresses = '*'
port = 5432
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix


```



============================================================

### Файл: `init-scripts/init.sql`


```sql

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


```

