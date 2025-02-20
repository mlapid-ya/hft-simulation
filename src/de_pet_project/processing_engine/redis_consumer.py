import time
import json
import asyncio
from loguru import logger
import redis.asyncio as redis

from de_pet_project.shared_utils.order_book import OrderBook
from de_pet_project.shared_utils.redis_client import RedisClient

class RedisConsumer(RedisClient):

    def __init__(self, stream_name: str, group_name: str, consumer_name: str):
        super().__init__(stream_name)

        self.group_name: str = group_name
        self.consumer_name: str = consumer_name

    async def __ainit__(self) -> None:
        await super().__ainit__()
        await self._create_consumer_group()

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
                        data: str = message_data[b'message'].decode('utf-8')
                        data: dict = json.loads(data)

                        await self._redis_client.xack(self.stream_name, self.group_name, message_id)
                        await self._redis_client.xdel(self.stream_name, message_id)

                        await self.process_message(data)

                        # latency: float = ts_received - message_data['ts_sent']

                        # logger.info(f"Latency: {latency}")
            else:
                logger.info("No new messages. Waiting for more...")
                await asyncio.sleep(5)

    async def process_message(self, data: dict) -> None:
        '''
        data: dict = {
            'channel': str,
            'ts_received': float,
            'ts_sent': float,
            'offset': float,
            'data': dict
        }
        '''

        logger.info(f"Data: {data}")

    async def close(self) -> None:
        await self._redis_client.aclose()
        logger.info(f"{self} is closed.")