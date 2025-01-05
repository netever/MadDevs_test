# Используем официальный образ Python
FROM python:3.11-slim

# Установка необходимых системных пакетов
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && echo "export PATH=/root/.local/bin:\$PATH" >> /root/.bashrc \
    && /root/.local/bin/poetry config virtualenvs.create false

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY . .

# Установка зависимостей
RUN /root/.local/bin/poetry install --no-interaction --no-root

# Установка переменных окружения
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# Установка проекта
RUN /root/.local/bin/poetry install --no-interaction

# Команда по умолчанию
CMD ["poetry", "run", "python", "src/main.py", "--max-len=4096", "input/source.html"]
