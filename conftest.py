# conftest.py — находится в КОРНЕ проекта (рядом с папкой app/)
# Этот файл автоматически добавляет корень проекта в sys.path,
# чтобы pytest мог найти модуль 'app' на любой ОС (Windows, Linux, macOS)

import sys
from pathlib import Path

# Добавляем корень проекта в начало пути поиска модулей
sys.path.insert(0, str(Path(__file__).parent))
