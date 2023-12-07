import os
from datetime import timedelta

from celery import Celery
from dotenv import load_dotenv
from loguru import logger

from db.engine import get_db
from db.models import MessageModel

load_dotenv()
broker_url = os.getenv("BROKER_URL", default="pyamqp://guest:guest@localhost//")

celery = Celery("tasks", broker=broker_url)


celery.conf.update(
    result_backend="rpc://",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)
celery.conf.beat_schedule = {
    "get_message_task": {
        "task": "tasks.get_message_from_rabbit",
        "schedule": timedelta(seconds=180),
    },
}


@celery.task
async def get_message_from_rabbit(title, datetime, text):
    try:
        message = MessageModel(title=title, datetime=datetime, text=text)
        db_session = get_db()
        db_session.add(message)
        db_session.commit()
        logger.info("Сообщение успешно обработано")
    except Exception as e:
        logger.warning(f"Ошибка обработки сообщения: {e}")
