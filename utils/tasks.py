from datetime import timedelta

from celery import Celery
from loguru import logger

from db.engine import get_db
from db.models import MessageModel
from config import BROKER_URL

celery = Celery("tasks", broker=BROKER_URL)


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
