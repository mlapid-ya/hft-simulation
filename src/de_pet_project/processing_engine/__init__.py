import asyncio

from loguru import logger

from de_pet_project.processing_engine.redis_consumer import RedisConsumer

async def run():
    stream_name = 'deribit_connector'
    group_name = 'deribit_connector_consumer_group'
    consumer_name = 'deribit_connector_consumer'

    redis_consumer: RedisConsumer = RedisConsumer(
        stream_name=stream_name,
        group_name=group_name,
        consumer_name=consumer_name
    )

    await redis_consumer.__ainit__()

    try:
        async with asyncio.TaskGroup() as deribit_consumer:
            deribit_consumer.create_task(redis_consumer.consume_messages())
    except asyncio.CancelledError:
        logger.info("Closing the consumer.")
        await redis_consumer.close()

def main():
    asyncio.run(run())
