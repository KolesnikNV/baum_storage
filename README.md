![Python](https://img.shields.io/badge/python-blue)
![Asyncio](https://img.shields.io/badge/asyncio-green)
![FastAPI](https://img.shields.io/badge/fastapi-red)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-yellow)
![Alembic](https://img.shields.io/badge/alembic-green)
![PostgreSQL](https://img.shields.io/badge/postgres-blue)
![Celery](https://img.shields.io/badge/celery-green)
![RabbitMQ](https://img.shields.io/badge/rabbitmq-red)

## Установка
1) Клонируйте репозиторий ```git clone https://github.com/KolesnikNV/baum_storage.git```
2) Запустите docker-compose.yml ```docker-compose up --build -d```

## Работа
Код предназначен для загрузки текста через API, парсинга строк этого текста и добавления данных в БД через Celery и RabbitMQ

- эндпоинт ```api/upload-text/``` предназначен для загрузки текста 
- эндпоинт ```api/results/``` предназначен для построчного получения текста