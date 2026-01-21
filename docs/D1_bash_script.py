#!/usr/bin/env python3
"""
Спринт D1: Проверка работы Docker
Скрипт проверяет работоспособность Docker и подготавливает окружение для PostgreSQL.
"""

import subprocess
import os
import sys
import time
from pathlib import Path

# ==============================
# Конфигурация из settings.md
# ==============================
PROJECT_ROOT = "/postgres"
PROJECT_DIR = os.path.join(PROJECT_ROOT, "project")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
LOG_FILE = os.path.join(DOCS_DIR, "D1_logs.md")

# Создаём необходимые каталоги
os.makedirs(PROJECT_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# ==============================
# Утилиты
# ==============================
def run_command(cmd, description):
    """Выполняет команду и возвращает результат"""
    print(f"▶ {description}")
    print(f"  Команда: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        success = result.returncode == 0
        output = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr else ""
        
        log_entry = f"""
## {description}
**Команда:** `{cmd}`
**Статус:** {'✅ Успешно' if success else '❌ Ошибка'}
**Код возврата:** {result.returncode}
**Вывод:** {output}
"""
        if error:
            log_entry += f"""**Ошибки:** {error} """
        
        return success, log_entry, output, error
    
    except Exception as e:
        error_msg = f"Исключение при выполнении команды: {str(e)}"
        log_entry = f"""
## {description}
**Команда:** `{cmd}`
**Статус:** ❌ Исключение
**Ошибка:** {error_msg}
"""
        return False, log_entry, "", error_msg

def write_log(header, content):
    """Записывает лог в файл"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(header)
        f.write(content)

# ==============================
# Основной скрипт
# ==============================
def main():
    print("=" * 60)
    print("Спринт D1: Проверка работы Docker")
    print("=" * 60)
    
    # Очищаем старый лог-файл или создаём новый
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("# Логи выполнения спринта D1\n\n")
        f.write(f"**Время начала:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    all_tests_passed = True
    log_content = ""
    
    # ==============================
    # Задача 1: Проверка версии Docker и состояния
    # ==============================
    print("\n" + "=" * 40)
    print("ЗАДАЧА 1: Проверка Docker")
    print("=" * 40)
    
    # 1.1 Проверка версии Docker
    success, log, output, _ = run_command(
        "docker --version",
        "Проверка версии Docker"
    )
    log_content += log
    if success:
        print(f"  ✅ Версия Docker: {output}")
    else:
        print("  ❌ Docker не установлен или недоступен")
        all_tests_passed = False
    
    # 1.2 Проверка состояния Docker
    success, log, output, _ = run_command(
        "docker info",
        "Проверка состояния Docker"
    )
    log_content += log
    if success:
        print("  ✅ Docker работает корректно")
    else:
        print("  ❌ Проблемы с Docker демоном")
        all_tests_passed = False
    
    # ==============================
    # Задача 2: Проверка образов
    # ==============================
    print("\n" + "=" * 40)
    print("ЗАДАЧА 2: Проверка образов Docker")
    print("=" * 40)
    
    success, log, output, _ = run_command(
        "docker images hello-world",
        "Проверка наличия образа hello-world"
    )
    log_content += log
    
    if "hello-world" in output:
        print("  ✅ Образ hello-world уже существует")
        image_exists = True
    else:
        print("  ℹ️  Образ hello-world отсутствует, будет загружен")
        image_exists = False
    
    # ==============================
    # Задача 3: Тестовый контейнер hello-world
    # ==============================
    print("\n" + "=" * 40)
    print("ЗАДАЧА 3: Запуск тестового контейнера")
    print("=" * 40)
    
    # Сначала загружаем образ, если его нет
    if not image_exists:
        success, log, output, _ = run_command(
            "docker pull hello-world",
            "Загрузка образа hello-world"
        )
        log_content += log
        if success:
            print("  ✅ Образ hello-world загружен")
        else:
            print("  ❌ Ошибка загрузки образа")
            all_tests_passed = False
    
    # Запускаем контейнер
    success, log, output, _ = run_command(
        "docker run --rm hello-world",
        "Запуск контейнера hello-world"
    )
    log_content += log
    
    if success and "Hello from Docker!" in output:
        print("  ✅ Контейнер hello-world успешно запущен")
    else:
        print("  ❌ Ошибка запуска контейнера hello-world")
        all_tests_passed = False
    
    # ==============================
    # Задача 4: Проверка монтирования томов
    # ==============================
    print("\n" + "=" * 40)
    print("ЗАДАЧА 4: Проверка монтирования томов")
    print("=" * 40)
    
    # Создаём тестовый том
    test_volume = "test_volume_d1"
    
    success, log, output, _ = run_command(
        f"docker volume create {test_volume}",
        f"Создание тестового тома '{test_volume}'"
    )
    log_content += log
    
    if success:
        print(f"  ✅ Том '{test_volume}' создан")
        
        # Проверяем, что том существует
        success, log, output, _ = run_command(
            f"docker volume inspect {test_volume}",
            f"Проверка создания тома '{test_volume}'"
        )
        log_content += log
        
        if success:
            print(f"  ✅ Том '{test_volume}' успешно создан и доступен")
        else:
            print(f"  ❌ Проблемы с томом '{test_volume}'")
            all_tests_passed = False
        
        # Очищаем тестовый том
        success, log, output, _ = run_command(
            f"docker volume rm {test_volume}",
            f"Удаление тестового тома '{test_volume}'"
        )
        log_content += log
        
        if success:
            print(f"  ✅ Том '{test_volume}' удалён")
        else:
            print(f"  ⚠️  Не удалось удалить том '{test_volume}'")
    
    else:
        print(f"  ❌ Не удалось создать том '{test_volume}'")
        all_tests_passed = False
    
    # ==============================
    # Задача 5: Подготовка каталога для PostgreSQL
    # ==============================
    print("\n" + "=" * 40)
    print("ЗАДАЧА 5: Подготовка каталога данных")
    print("=" * 40)
    
    data_dir = os.path.join(PROJECT_DIR, "data")
    
    # Создаём каталог
    try:
        os.makedirs(data_dir, exist_ok=True)
        
        # Проверяем создание
        if os.path.exists(data_dir):
            # Устанавливаем правильные права
            subprocess.run(f"chmod 755 {data_dir}", shell=True, check=False)
            
            success_msg = f"✅ Каталог создан: {data_dir}"
            print(f"  {success_msg}")
            
            log_entry = f"""
## Подготовка каталога для PostgreSQL
**Каталог:** `{data_dir}`
**Статус:** ✅ Успешно создан
**Права:** `{oct(os.stat(data_dir).st_mode)[-3:]}`
"""
            log_content += log_entry
        else:
            error_msg = f"❌ Не удалось создать каталог: {data_dir}"
            print(f"  {error_msg}")
            log_content += f"\n## Ошибка создания каталога\n\n{error_msg}\n"
            all_tests_passed = False
    
    except Exception as e:
        error_msg = f"❌ Ошибка при создании каталога: {str(e)}"
        print(f"  {error_msg}")
        log_content += f"\n## Ошибка создания каталога\n\n{error_msg}\n"
        all_tests_passed = False
    
    # ==============================
    # Итоги
    # ==============================
    print("\n" + "=" * 60)
    print("ИТОГИ ВЫПОЛНЕНИЯ СПРИНТА D1")
    print("=" * 60)
    
    if all_tests_passed:
        final_status = "✅ ВСЕ ЗАДАЧИ ВЫПОЛНЕНЫ УСПЕШНО"
        print(final_status)
    else:
        final_status = "❌ ЕСТЬ ПРОБЛЕМЫ, ТРЕБУЕТСЯ ДОРАБОТКА"
        print(final_status)
    
    # Записываем все логи в файл
    write_log(f"\n## Итоговый статус: {final_status}\n\n", log_content)
    
    # Добавляем время завершения
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n**Время завершения:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\nЛоги сохранены в: {LOG_FILE}")
    
    # Возвращаем код завершения
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())
