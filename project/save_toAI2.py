#!/usr/bin/env python3
"""
Скрипт для сбора содержимого файлов и каталогов в один файл toAI.md
Игнорирует архивные файлы, ограничивает вывод 1000 строк
"""

import os
import mimetypes
import sys
from pathlib import Path

# Расширения архивных файлов для игнорирования
ARCHIVE_EXTENSIONS = {
    '.zip', '.tar', '.gz', '.bz2', '.xz', '.rar', '.7z', 
    '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2'
}

# Расширения бинарных/исполняемых файлов для игнорирования
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.pyc', '.pyo',
    '.pyd', '.class', '.jar', '.war', '.ear', '.apk', '.ipa',
    '.app', '.dmg', '.iso', '.img', '.o', '.obj', '.lib', '.a'
}

# Файлы и каталоги, которые нужно игнорировать
IGNORED_ITEMS = {
    '.git', '.svn', '.hg', '__pycache__', 'node_modules',
    'venv', '.venv', 'env', '.env', 'toAI.md', '.DS_Store',
    'Thumbs.db', 'desktop.ini', 'save_toAI.py', 'save_toAI2.py', 'toAI.md'
}

def is_archive_or_binary(filepath):
    """Проверяет, является ли файл архивом или бинарным файлом"""
    ext = Path(filepath).suffix.lower()
    
    # Проверка по расширению
    if ext in ARCHIVE_EXTENSIONS or ext in BINARY_EXTENSIONS:
        return True
    
    # Проверка по MIME-типу
    try:
        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type:
            if mime_type.startswith('application/') and any(
                archive in mime_type for archive in ['zip', 'rar', '7z', 'tar', 'gzip']
            ):
                return True
            if mime_type.startswith('application/octet-stream'):
                return True
    except:
        pass
    
    # Эвристическая проверка на бинарный файл
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:  # Нулевые байты часто встречаются в бинарных файлах
                return True
    except:
        pass
    
    return False

def read_file_content(filepath, max_lines=500):
    """Читает содержимое файла с ограничением по количеству строк"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"\n... [файл обрезан, показано {max_lines} из ... строк]\n")
                    break
                lines.append(line)
            return ''.join(lines)
    except UnicodeDecodeError:
        try:
            # Пробуем другую кодировку
            with open(filepath, 'r', encoding='latin-1', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append(f"\n... [файл обрезан, показано {max_lines} из ... строк]\n")
                        break
                    lines.append(line)
                return ''.join(lines)
        except:
            return "[Не удалось прочитать файл (возможно, бинарный)]\n"
    except Exception as e:
        return f"[Ошибка при чтении файла: {str(e)}]\n"

def get_directory_structure():
    """Возвращает структуру каталогов и файлов в виде markdown"""
    structure_lines = []
    
    # Собираем все элементы для отображения
    all_items = []
    ignored_count = 0
    
    for root, dirs, files in os.walk('.'):
        # Фильтруем игнорируемые каталоги
        original_dirs = dirs.copy()
        dirs[:] = [d for d in dirs if d not in IGNORED_ITEMS]
        ignored_count += len([d for d in original_dirs if d in IGNORED_ITEMS])
        
        # Относительный путь
        rel_root = Path(root).relative_to('.') if root != '.' else Path('.')
        
        # Добавляем текущую директорию как заголовок
        if root == '.':
            structure_lines.append("## Структура проекта\n\n")
            structure_lines.append("```\n")
        
        # Вычисляем отступ для текущего уровня
        level = 0 if root == '.' else len(rel_root.parts)
        indent = "  " * level
        
        # Добавляем каталоги
        for d in sorted(dirs):
            structure_lines.append(f"{indent}📁 {d}/\n")
        
        # Добавляем файлы (кроме игнорируемых и архивных)
        for f in sorted(files):
            if f in IGNORED_ITEMS:
                ignored_count += 1
                continue
            
            filepath = Path(root) / f
            if is_archive_or_binary(filepath):
                ignored_count += 1
                continue
            
            if f == 'toAI.md':
                ignored_count += 1
                continue
            
            # Определяем иконку по типу файла
            ext = Path(f).suffix.lower()
            icon = "📄"  # обычный файл
            
            if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs']:
                icon = "📝"  # код
            elif ext in ['.md', '.txt', '.rst', '.tex']:
                icon = "📃"  # документ
            elif ext in ['.json', '.xml', '.yaml', '.yml', '.toml']:
                icon = "⚙️"  # конфигурация
            elif ext in ['.html', '.css', '.jsx', '.tsx']:
                icon = "🌐"  # веб
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico']:
                icon = "🖼️"  # изображение
            
            structure_lines.append(f"{indent}{icon} {f}\n")
    
    structure_lines.append("```\n\n")
    
    # Добавляем информацию об игнорированных элементах
    if ignored_count > 0:
        structure_lines.append(f"*Примечание: пропущено {ignored_count} игнорируемых элементов "
                              f"(архивы, бинарные файлы, служебные каталоги)*\n\n")
    
    structure_lines.append("---\n\n")
    
    return ''.join(structure_lines)

def collect_files():
    """Собирает все файлы и их содержимое"""
    current_dir = Path('.')
    all_content = []
    total_lines = 0
    
    # Заголовок документа
    all_content.append("# Анализ проекта\n\n")
    all_content.append(f"**Текущий каталог:** `{current_dir.absolute()}`\n\n")
    
    # Добавляем структуру каталогов
    all_content.append(get_directory_structure())
    
    # Заголовок для содержимого файлов
    all_content.append("## Содержимое файлов\n\n")
    
    # Рекурсивный обход каталогов для сбора содержимого файлов
    for root, dirs, files in os.walk('.'):
        # Игнорируем служебные каталоги
        dirs[:] = [d for d in dirs if d not in IGNORED_ITEMS]
        
        for filename in files:
            # Пропускаем игнорируемые файлы
            if filename in IGNORED_ITEMS:
                continue
            
            filepath = Path(root) / filename
            
            # Пропускаем архивные и бинарные файлы
            if is_archive_or_binary(filepath):
                continue
            
            # Пропускаем сам файл toAI.md
            if filename == 'toAI.md':
                continue
            
            # Читаем содержимое файла
            rel_path = filepath.relative_to('.')
            content = read_file_content(filepath)
            
            # Подсчитываем строки
            content_lines = content.count('\n') + 1
            total_lines += content_lines
            
            # Проверяем ограничение в 1000 строк
            if total_lines > 1000:
                all_content.append(f"\n## ⚠️ ВНИМАНИЕ: Превышено ограничение в 1000 строк\n")
                all_content.append(f"Текущее количество строк: {total_lines}\n")
                all_content.append(f"Сбор данных остановлен на файле: `{rel_path}`\n")
                return '\n'.join(all_content), total_lines, True
            
            # Добавляем разделитель и информацию о файле
            all_content.append(f"\n{'='*60}\n")
            all_content.append(f"### Файл: `{rel_path}`\n\n")
            
            # Добавляем содержимое файла в блок кода с указанием расширения
            ext = Path(filename).suffix
            lang = ext[1:] if ext else 'text'
            all_content.append(f"```{lang}\n")
            all_content.append(content)
            if not content.endswith('\n'):
                all_content.append('\n')
            all_content.append("```\n\n")
    
    return '\n'.join(all_content), total_lines, False

def main():
    """Основная функция"""
    print("Начинаю сбор файлов для анализа...")
    
    # Создаем новый файл (перезаписываем, если существует)
    # Это автоматически очищает файл при создании
    with open('toAI.md', 'w', encoding='utf-8') as f:
        f.write('')  # Создаем пустой файл
    
    # Собираем содержимое
    content, total_lines, exceeded = collect_files()
    
    # Записываем результат (полная перезапись)
    with open('toAI.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Файл toAI.md успешно создан/перезаписан!")
    print(f"📊 Количество строк: {total_lines}")
    if exceeded:
        print("⚠️  ВНИМАНИЕ: Превышено ограничение в 1000 строк!")
        print("   Файл был обрезан. Рассмотрите возможность исключения некоторых файлов.")
    else:
        print("✓ Уложились в ограничение 1000 строк")
    
    print(f"\n📄 Файл готов для отправки в ИИ: {os.path.abspath('toAI.md')}")

if __name__ == "__main__":
    main()