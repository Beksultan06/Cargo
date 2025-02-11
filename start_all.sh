!/bin/bash

Активируем виртуальное окружение
source /home/cargo/venv/bin/activate

# Запуск Uvicorn в фоне
uvicorn core.asgi:application --workers 3 --uds /home/cargo/uvicorn.sock &

# Запуск бота
python manage.py run
