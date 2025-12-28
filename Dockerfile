# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем директорию приложения
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директории для статических файлов и медиа
RUN mkdir -p staticfiles media logs

# Устанавливаем переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=site1.settings
ENV DEBUG=False
ENV SECRET_KEY=django-insecure-default-key-change-in-production

# Выполняем миграции и собираем статические файлы
RUN python manage.py collectstatic --noinput --clear && \
    python manage.py migrate --run-syncdb

# Создаем непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Временный healthcheck - просто проверяем что процесс работает
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep gunicorn || exit 1

# Команда запуска с gunicorn для продакшена
CMD sh -c "echo 'Starting Django on port $PORT' && echo 'PORT value: $PORT' && gunicorn --log-level debug --access-logfile - --error-logfile - site1.wsgi:application --bind 0.0.0.0:$PORT"
