import time
import json
import asyncio
from loguru import logger

from de_pet_project.shared_utils.redis_client import RedisClient
from de_pet_project.processing_engine.utils.stream_processor import StreamProcessor

class RedisConsumer(RedisClient):

    def __init__(self, stream_name: str, group_name: str, consumer_name: str):
        super().__init__(stream_name)

        self.group_name: str = group_name
        self.consumer_name: str = consumer_name

        self.message_processor: StreamProcessor = StreamProcessor(stream_name=self.stream_name)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(stream_name={self.stream_name}, group_name={self.group_name}, consumer_name={self.consumer_name})"

    async def __ainit__(self) -> None:
        try:
            await super().__ainit__()
            await self._create_consumer_group()
            await self.message_processor.__ainit__()
        except Exception as e:
            logger.error(f"Failed to initialize {self}: {e}")
            raise e
        else:
            logger.info(f"{self} is initialized.")

    async def _create_consumer_group(self) -> None:
        try:
            await self._redis_client.xgroup_create(self.stream_name, self.group_name, id='0', mkstream=True)
        except Exception as e:
            if "BUSYGROUP Consumer Group name already exists" not in str(e):
                raise

    async def consume_messages(self) -> None:
        while self.is_connected:
            messages: list = await self._redis_client.xreadgroup(
                groupname=self.group_name,
                consumername=self.consumer_name,
                streams={self.stream_name: '>'},
                count=1,
                block=100
            )

            if messages:
                ts_received: float = time.time()

                for stream, message_list in messages:
                    for message_id, message_data in message_list:
                        message_id: str = message_id.decode('utf-8')
                        message: str = message_data[b'message'].decode('utf-8')
                        message: dict = json.loads(message)

                        await self._redis_client.xack(self.stream_name, self.group_name, message_id)
                        await self._redis_client.xdel(self.stream_name, message_id)

                        await self.message_processor.process_message(message)
            else:
                logger.info("No new messages. Waiting for more...")
                await asyncio.sleep(5)

    async def close(self) -> None:
        await self._redis_client.aclose()
        await self.message_processor.close()
        logger.info(f"{self} is closed.")