import os
from asyncio import run

import pika
import uvicorn
from fastapi import FastAPI
from loguru import logger

from db.engine import get_db
from handlers.message_handler import message_router
from utils.rabbit_reciever import DeadLetterConsumer, MessageConsumer

app = FastAPI(
    title="Baum Storage",
    description="Baum Storage",
    version="0.1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.include_router(message_router, prefix="/api/", tags=["store"])


async def start_rabbit():
    cred = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq", virtual_host="/", credentials=cred)
    )
    channel = connection.channel()
    message_consumer = MessageConsumer(channel, get_db())
    dlx_consumer = DeadLetterConsumer(channel)
    channel.exchange_declare(exchange="dlx", exchange_type="direct")
    channel.queue_declare(queue="dlx_queue", durable=True)
    channel.queue_bind(exchange="dlx", queue="dlx_queue")

    queues = ["message_queue"]
    for queue in queues:
        channel.queue_declare(
            queue=queue,
            durable=True,
            arguments={
                "x-message-ttl": 5000,
                "x-dead-letter-exchange": "dlx",
                "x-dead-letter-routing-key": "dlx_queue",
            },
        )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue="message_queue",
        on_message_callback=message_consumer.consume,
        auto_ack=False,
    )
    channel.basic_consume(
        queue="dlx_queue",
        on_message_callback=dlx_consumer.consume,
        auto_ack=False,
    )
    channel.start_consuming()


async def main():
    await start_rabbit()
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        log_level="info",
        reload=True,
    )


if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        logger.info("Сервер останволен")
