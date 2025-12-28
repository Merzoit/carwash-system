# 🚀 Развертывание системы управления автомойкой

## 📋 Быстрый старт

### Требования
- Python 3.8+
- PostgreSQL (рекомендуется) или SQLite
- Git

### Локальная установка

```bash
# 1. Клонируем репозиторий
git clone https://github.com/Merzoit/carwash-system.git
cd carwash-system

# 2. Создаем виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# 3. Устанавливаем зависимости
pip install -r requirements.txt

# 4. Выполняем миграции
python manage.py migrate

# 5. Создаем суперпользователя
python manage.py createsuperuser

# 6. Запускаем сервер
python manage.py runserver
```

Откройте http://127.0.0.1:8000 в браузере.

## 🌐 Развертывание в сети

### 1. 🐳 Docker (Рекомендуется для большинства случаев)

#### Развертывание с Docker Compose
```bash
# Клонируем репозиторий
git clone https://github.com/Merzoit/carwash-system.git
cd carwash-system

# Создаем .env файл
cp env.example .env
# Отредактируйте .env файл с вашими настройками

# Запускаем с PostgreSQL и Redis
docker-compose up -d

# Приложение будет доступно на http://localhost:8000
```

#### Только приложение (без базы данных)
```bash
# Запускаем только веб-приложение
docker build -t carwash-app .
docker run -p 8000:8000 --env-file .env carwash-app
```

### 2. 🚀 Heroku (Рекомендуется для начала)

#### Создание приложения
```bash
# Устанавливаем Heroku CLI
# Создаем приложение
heroku create your-carwash-app

# Добавляем PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Настраиваем переменные окружения
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-super-secret-key-here
heroku config:set ALLOWED_HOSTS=your-carwash-app.herokuapp.com

# Деплоим
git push heroku main

# Выполняем миграции
heroku run python manage.py migrate

# Создаем суперпользователя
heroku run python manage.py createsuperuser
```

#### Файлы для Heroku
Создайте `Procfile`:
```
web: gunicorn site1.wsgi --log-file -
```

И `runtime.txt`:
```
python-3.11.7
```

### 2. 🐳 Railway (Рекомендуется)

Railway автоматически поддерживает Docker и предоставляет бесплатный тариф.

#### Настройка Railway:

1. **Создайте аккаунт** на [Railway.app](https://railway.app)
2. **Подключите GitHub** репозиторий
3. **Railway автоматически** обнаружит Dockerfile и соберет приложение
4. **Добавьте переменные окружения** в Settings проекта:

```env
DEBUG=False
SECRET_KEY=ваш-супер-секретный-ключ-здесь
ALLOWED_HOSTS=*.railway.app,your-project-name.up.railway.app
```

5. **Railway автоматически** создаст домен типа `your-project-name.up.railway.app`

#### Переменные окружения для Railway:

```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=*.railway.app,your-project-name.up.railway.app
TIME_ZONE=Europe/Moscow
LANGUAGE_CODE=ru-ru
```

#### Решение проблем с Railway:

**Ошибка 400 (Bad Request):**
- Проверьте `ALLOWED_HOSTS` - должен включать `*.railway.app`
- Добавьте `CSRF_TRUSTED_ORIGINS` в settings.py

**Ошибка с доменом:**
- Домен генерируется автоматически после успешного деплоя
- Проверьте раздел "Settings → Domains"

**База данных:**
- Railway автоматически предоставляет PostgreSQL
- `DATABASE_URL` устанавливается автоматически

### 3. 🐙 VPS с Ubuntu

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python и PostgreSQL
sudo apt install python3 python3-pip postgresql postgresql-contrib nginx -y

# Клонируем проект
git clone https://github.com/Merzoit/carwash-system.git
cd carwash-system

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Настраиваем базу данных
sudo -u postgres createdb carwash_db
sudo -u postgres createuser --interactive --pwprompt carwash_user

# Выполняем миграции
python manage.py migrate

# Собираем статические файлы
python manage.py collectstatic

# Создаем суперпользователя
python manage.py createsuperuser

# Запускаем сервер
python manage.py runserver 0.0.0.0:8000
```

### 4. 📦 PythonAnywhere

1. Создайте аккаунт на PythonAnywhere
2. Создайте новое веб-приложение
3. Выберите Django
4. Клонируйте репозиторий в консоли PythonAnywhere
5. Настройте переменные окружения в настройках веб-приложения
6. Выполните миграции через консоль

## ⚙️ Настройки для продакшена

### Переменные окружения (.env)

```env
# Django настройки
DEBUG=False
SECRET_KEY=ваш-супер-секретный-ключ-здесь
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/carwash_db

# Email (опционально)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Другие настройки
TIME_ZONE=Europe/Moscow
LANGUAGE_CODE=ru-ru
```

### Безопасность

1. **Измените SECRET_KEY** на сложную строку
2. **Настройте HTTPS** (Let's Encrypt для бесплатных сертификатов)
3. **Ограничьте ALLOWED_HOSTS** только вашими доменами
4. **Регулярно обновляйте** зависимости

### Оптимизация

1. **Используйте PostgreSQL** вместо SQLite
2. **Настройте кэширование** (Redis)
3. **Оптимизируйте статические файлы** (CDN)
4. **Настройте логирование**

## 🔍 Мониторинг и поддержка

### Логи
```bash
# Просмотр логов Django
python manage.py log

# На Heroku
heroku logs --tail

# На Railway
railway logs
```

### Резервное копирование
```bash
# Создание бэкапа базы данных
pg_dump carwash_db > backup.sql

# Восстановление
psql carwash_db < backup.sql
```

## 🆘 Решение проблем

### Ошибка "DisallowedHost"
- Проверьте ALLOWED_HOSTS в настройках

### Ошибка базы данных
- Убедитесь, что база данных запущена
- Проверьте DATABASE_URL

### Статические файлы не загружаются
- Выполните `python manage.py collectstatic`
- Проверьте STATIC_ROOT и STATIC_URL

### Проблемы с миграциями
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --run-syncdb
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи приложения
2. Посмотрите документацию в разделе "Помощь"
3. Создайте Issue на GitHub

---

**🚀 Удачного развертывания!**
