#!/bin/bash

# Скрипт для развертывания на Linux сервере

echo "🚀 Начинаем развертывание на сервере..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker:"
    echo "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose"
    exit 1
fi

# Клонируем репозиторий (если не существует)
if [ ! -d "carwash-system" ]; then
    echo "📥 Клонируем репозиторий..."
    git clone https://github.com/Merzoit/carwash-system.git
    cd carwash-system
else
    cd carwash-system
    echo "📥 Обновляем репозиторий..."
    git pull origin main
fi

# Создаем .env файл если не существует
if [ ! -f ".env" ]; then
    echo "📝 Создаем .env файл..."
    cp env.example .env
    echo "⚠️  Отредактируйте .env файл с вашими настройками!"
    echo "nano .env"
    read -p "Нажмите Enter после редактирования .env файла..."
fi

# Собираем и запускаем контейнеры
echo "🐳 Запускаем приложение..."
docker-compose down 2>/dev/null
docker-compose up --build -d

# Ждем запуска
echo "⏳ Ждем запуска приложения..."
sleep 30

# Проверяем статус
if docker-compose ps | grep -q "Up"; then
    echo "✅ Приложение успешно запущено!"
    echo ""
    echo "🌐 Доступно по адресу: http://$(curl -s ifconfig.me):8000"
    echo "🔧 Для просмотра логов: docker-compose logs -f web"
    echo "🛑 Для остановки: docker-compose down"
else
    echo "❌ Ошибка запуска. Проверьте логи:"
    docker-compose logs web
fi
