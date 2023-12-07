import json
import random
import time

from loguru import logger

from utils.tasks import get_message_from_rabbit
from .rabbit_exceptions import DeadLetterError

logger.add("log.txt", format="{time} | {level} | {message}")


class Consumer:
    MAX_RETRIES = 2
    RETRY_DELAY_SECONDS = 1

    def message_can_be_retried(self, properties):
        deaths = (properties.headers or {}).get("x-death")
        return deaths[0]["count"] < self.MAX_RETRIES if deaths else True

    def retry(self):
        logger.info(
            f"Повторная попытка обработки через {self.RETRY_DELAY_SECONDS} секунд"
        )
        time.sleep(self.RETRY_DELAY_SECONDS)


class MessageConsumer(Consumer):
    def __init__(self, channel, db_session):
        self.channel = channel
        self.db_session = db_session

    def consume(self, channel, method, properties, body):
        try:
            data = json.loads(body)
            title = data["title"]
            datetime = data["datetime"]
            text = data["text"]
            get_message_from_rabbit.delay(title, datetime, text)
            channel.basic_ack(delivery_tag=method.delivery_tag)

        except Exception:
            logger.warning("Ошибка обработки сообщения")
            if self.message_can_be_retried(properties):
                channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                self.retry()
            else:
                logger.info("Сообщение не было доставлено")
                channel.basic_ack(delivery_tag=method.delivery_tag)


class DeadLetterConsumer(Consumer):
    def __init__(self, channel):
        self.channel = channel

    def consume(self, channel, method, properties):
        try:
            if random.choice([True, False]):
                raise DeadLetterError(
                    "Ошибка при отправке сообщения из мертвой очереди"
                )
            logger.info("Сообщение из мертвой очереди обработалось")
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(e)
            if self.message_can_be_retried(properties):
                channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                self.retry()
            else:
                logger.warning("Cообщение не было доставлено из мертвой очереди")
                channel.basic_ack(delivery_tag=method.delivery_tag)
