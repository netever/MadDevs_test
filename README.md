# HTML Fragmenter

Инструмент для разделения HTML-сообщений на фрагменты с сохранением валидной структуры тегов. Разработан для решения проблемы ограничения длины сообщений (4096 символов) в корпоративном мессенджере.

## Возможности

- Разделение HTML-сообщений на фрагменты заданной длины
- Сохранение структуры HTML-тегов в каждом фрагменте
- Корректная обработка вложенных блоков
- Поддержка блочных тегов: `<p>`, `<b>`, `<strong>`, `<i>`, `<ul>`, `<ol>`, `<div>`, `<span>`

## Структура проекта

```
html-fragmenter/
├── src/                    # Исходный код
│   ├── main.py            # Основной скрипт для запуска
│   └── html_fragmenter/   # Модуль фрагментации
│       ├── msg_split.py   # Логика разделения HTML
│       └── exceptions.py  # Пользовательские исключения
├── tests/                 # Тесты
│   ├── test_msg_split.py
│   └── data/             # Тестовые данные
├── Dockerfile            # Конфигурация Docker
├── pyproject.toml        # Конфигурация Poetry
└── requirements.txt      # Зависимости для pip
```

## Установка

### Используя Poetry (рекомендуется)

```bash
# Установка Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Установка зависимостей
poetry install

# Активация виртуального окружения
poetry shell
```

### Используя pip

```bash
pip install -r requirements.txt
```

### Используя Docker

```bash
# Сборка образа
docker build -t html-fragmenter .

# или с использованием docker-compose
docker-compose up --build
```

## Использование

### Запуск через Poetry

```bash
poetry run python src/main.py --max-len=4096 input/source.html
```

### Запуск через pip

```bash
python src/main.py --max-len=4096 input/source.html
```

### Запуск через Docker

```bash
docker run html-fragmenter poetry run python src/main.py --max-len=4096 input/source.html
```

## Параметры командной строки

- `input_file`: путь к входному HTML-файлу (обязательный параметр)
- `--max-len`: максимальная длина фрагмента (по умолчанию 4096)

## Примеры

### Простой HTML-файл

```bash
poetry run python src/main.py --max-len=3072 input/source.html
```

Вывод будет содержать фрагменты с указанием их длины:
```
-- fragment #1: 2048 chars --
<html>...</html>

-- fragment #2: 1024 chars --
<html>...</html>
```

## Разработка

### Запуск тестов

```bash
# Через Poetry
poetry run pytest

# Через Docker
docker run html-fragmenter
```

## Зависимости

- Python ≥ 3.8
- beautifulsoup4: для парсинга HTML
- click: для работы с CLI
- lxml: быстрый парсер HTML