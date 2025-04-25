# ToDo API на FastAPI с PostgreSQL

Простое API для управления списком задач с использованием FastAPI и PostgreSQL. Проект готов к развертыванию через Docker.

📋 Функционал

    CRUD операции для задач

    Фильтрация задач по:

        Статусу выполнения

        Сроку выполнения

        Поиск в названии

    Автоматическая документация (Swagger/Redoc)

    Готовые тесты API и БД

🛠 Технологии

    Python 3.9

    FastAPI

    PostgreSQL

    Docker + Docker Compose

    Pytest (для тестирования)

🚀 Быстрый старт
Предварительные требования

    Установленный Docker и Docker Compose

    Порт 8000 и 5432 свободны

Запуск проекта

    Клонируйте репозиторий:

bash

git clone https://github.com/NadyaMamonova/Todo_api.git

cd todo_api

    Запустите проект:

    bash

    docker-compose up --build -d

Приложение будет доступно по адресу:

    API: http://localhost:8000

    Swagger UI: http://localhost:8000/docs

    Redoc: http://localhost:8000/redoc

🏗 Структура проекта

todo_api/
├── app/
│   ├── crud.py        # Логика работы с БД
│   ├── database.py    # Подключение к БД
│   ├── main.py        # FastAPI приложение
│   ├── models.py      # Pydantic модели
├── tests/
│   ├── test_api.py    # Тесты API
│   ├── test_db.py     # Тесты БД
├── migrations/
│   └── init.sql       # SQL-миграции
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

📚 Документация API

Все эндпоинты доступны через Swagger UI: http://localhost:8000/docs
Основные эндпоинты:

    POST /tasks/ - Создать задачу

    GET /tasks/ - Получить список задач (с фильтрами)

    GET /tasks/{task_id} - Получить задачу по ID

    PUT /tasks/{task_id} - Обновить задачу

    DELETE /tasks/{task_id} - Удалить задачу

🧪 Тестирование

Для запуска тестов:

    bash

    docker-compose up tests

Или локально (если БД запущена):
    
    bash

    pytest tests/

⚙️ Настройки окружения

Переменные окружения в docker-compose.yml:

    DATABASE_URL - URL подключения к PostgreSQL

    PYTHONPATH - Путь для импортов Python

🔄 Обновление проекта

    Остановите контейнеры:

    bash

    docker-compose down

Пересоберите образы:

    bash

    docker-compose build --no-cache

Запустите заново:

    bash

    docker-compose up -d

🛠 Устранение неполадок

Если приложение не запускается:

Проверьте логи:

    bash

    docker-compose logs app

Проверьте подключение к БД:

    bash

    docker-compose exec db psql -U postgres -d todo_db -c "\dt"

Очистите volumes и перезапустите:

    bash

    docker-compose down -v
    docker-compose up --build