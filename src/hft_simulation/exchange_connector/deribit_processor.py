import time
from datetime import datetime

from loguru import logger

from hft_simulation.shared_utils.message_processor import MessageProcessor
from hft_simulation.shared_utils.grafana_connector import GrafanaConnector
from hft_simulation.exchange_connector.utils.redis_producer import RedisProducer
from hft_simulation.shared_utils.order_book import OrderBook

class DeribitProcessor(MessageProcessor):
    def __init__(self, stream_name: str):
        super().__init__(stream_name=stream_name)

        self.redis_producer: RedisProducer = RedisProducer(stream_name=self.stream_name)
        self.grafana_connector: GrafanaConnector = GrafanaConnector(stream_name=self.stream_name)

        self.ts_last_issued_order_book: float = None

    async def __ainit__(self) -> None:
        try:
            await self.grafana_connector.connect()
            await self.redis_producer.__ainit__()
        except Exception as e:
            logger.error(f"Failed to initialize {self}: {e}")
            raise e
        else:
            logger.info(f"{self} is initialized.")

    async def process_message(self, message: dict) -> None:
        ts_received: float = message['ts_received']
        offset: float = message['offset']
        channel: str = message['channel']
        data: dict = message['data']

        if 'book' in channel:
            channel = 'order_book'

            data['timestamp'] = data['timestamp'] / 1e3

            try:
                order_book: OrderBook = OrderBook(
                    timestamp=data['timestamp'],
                    instrument_name=data['instrument_name'],
                    bids=data['bids'],
                    asks=data['asks']
                )
            except Exception as e:
                logger.error(f"Error processing order book: {e}")
                return

            logger.info(f"Received message: {order_book.model_dump_json()}")

            if self.ts_last_issued_order_book is None:
                self.ts_last_issued_order_book = order_book.timestamp

            redis_data = {
                'channel': channel,
                'ts_received': ts_received,
                'ts_sent': time.time(),
                'offset': offset,
                'data': order_book.model_dump(mode='json')
            }

            await self.redis_producer.produce_message(redis_data)

            await self.grafana_connector.send(
                channel_name='exchange_connector',
                data = {
                    'delta_message_issued': (order_book.timestamp - self.ts_last_issued_order_book).total_seconds(),
                    'latency': (datetime.fromtimestamp(ts_received + offset) - order_book.timestamp).total_seconds(),
                    'queue_size': await self.redis_producer.stream_length()
                },
                timestamp=ts_received
            )

            self.ts_last_issued_order_book = order_book.timestamp
        
        else:
            logger.error(f"Unknown channel: {channel}")

    async def close(self) -> None:
        await self.redis_producer.close()
        await self.grafana_connector.close()
        logger.info(f"{self} is closed.")