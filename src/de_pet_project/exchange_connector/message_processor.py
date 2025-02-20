import time
import json

from loguru import logger

from de_pet_project.shared_utils.grafana_connector import GrafanaConnector
from de_pet_project.exchange_connector.utils.redis_producer import RedisProducer
from de_pet_project.shared_utils.order_book import OrderBook

class MessageProcessor:
    def __init__(self, stream_name: str):
        self.stream_name: str = stream_name

        self.redis_producer: RedisProducer = RedisProducer(stream_name=self.stream_name)
        self.grafana_connector: GrafanaConnector = GrafanaConnector(stream_name=self.stream_name)

        self.ts_last_issued_order_book: float = None

    async def __ainit__(self) -> None:
        try:
            await self.grafana_connector.__ainit__()
            await self.redis_producer.__ainit__()
        except Exception as e:
            logger.error(f"Failed to initialize {self}: {e}")
            raise e
        
    def __str__(self) -> str:
        return f"MessageProcessor(stream_name={self.stream_name})"
        
    async def close(self) -> None:
        await self.redis_producer.close()
        await self.grafana_connector.close()
        logger.info(f"{self} is closed.")

    async def process_message(self, message: dict) -> None:
        ts_received: float = message['ts_received']
        offset: float = message['offset']
        channel: str = message['channel']
        data: dict = message['data']

        if 'book' in channel:

            data['timestamp'] = data['timestamp'] / 1e3

            try:
                order_book: OrderBook = OrderBook(**data)
            except Exception as e:
                logger.error(f"Error processing order book: {e}")
                return

            logger.info(f"Received message: {order_book.model_dump_json()}")

            if self.ts_last_issued_order_book is None:
                self.ts_last_issued_order_book = order_book.timestamp

            redis_data = json.dumps(
                {
                    'channel': 'exchange_connector',
                    'ts_received': ts_received,
                    'ts_sent': time.time(),
                    'offset': offset,
                    'data': order_book.model_dump()
                }
            ).encode('utf-8')

            await self.redis_producer.produce_message(redis_data)

            await self.grafana_connector.send(
                channel_name='exchange_connector',
                data = {
                    'delta_message_issued': order_book.timestamp - self.ts_last_issued_order_book,
                    'latency': (ts_received + offset) - order_book.timestamp,
                    'queue_size': await self.redis_producer.stream_length()
                },
                timestamp=ts_received
            )

            self.ts_last_issued_order_book = order_book.timestamp
        
        else:
            logger.error(f"Unknown channel: {channel}")