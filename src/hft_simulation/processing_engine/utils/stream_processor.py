import time
import asyncio
from datetime import datetime

from loguru import logger

from hft_simulation.shared_utils.order_book import OrderBook
from hft_simulation.shared_utils.mongo_connector import MongoConnector
from hft_simulation.shared_utils.message_processor import MessageProcessor
from hft_simulation.shared_utils.grafana_connector import GrafanaConnector

class StreamProcessor(MessageProcessor):

    def __init__(self, stream_name: str):
        super().__init__(stream_name=stream_name)

        self.grafana_connector = GrafanaConnector(stream_name=self.stream_name)
        self.mongo_connector = MongoConnector()

        self.last_timestamp: datetime = None
        self.counter: int = 0

    async def __ainit__(self) -> None:
        try:
            await self.grafana_connector.__ainit__()
            await self.mongo_connector.connect()
        except Exception as e:
            logger.error(f"Failed to initialize {self}: {e}")
            raise e
        else:
            logger.info(f"{self} is initialized.")
    
    async def process_message(self, message: dict) -> bool:
        '''
        message: dict = {
            'channel': str,
            'ts_received': float,
            'ts_sent': float,
            'offset': float,
            'data': dict
        }
        '''
        ts_received: float = time.time()
        # logger.info(f"Message received: {message}")
        self.counter += 1
        logger.info(f"Messages received: {self.counter}")

        order_book: OrderBook = OrderBook(**message['data'])

        if self.last_timestamp is None:
            self.last_timestamp = order_book.timestamp
        else:
            if order_book.timestamp > self.last_timestamp:
                self.last_timestamp = order_book.timestamp
            else:
                logger.error(f"Order book timestamp is not increasing: {str(order_book.timestamp)} <= {str(self.last_timestamp)}")
                return False

        async with asyncio.Semaphore(1):
            await asyncio.gather(
                self.grafana_connector.send(
                    channel_name = 'processing_engine',
                    data = {
                        'delta_message_processed': ts_received - message['ts_sent'],
                    },
                    timestamp = ts_received
                ),
                self.grafana_connector.send(
                    channel_name = 'order_book',
                    data = {
                        'microprice': order_book.micro_price,
                        'volume_imbalance': order_book.volume_imbalance,
                        'volume_imbalance_total': order_book.volume_imbalance_total,
                        'spread': order_book.spread,
                    },
                    timestamp = order_book.timestamp.timestamp()
                ),
                self.mongo_connector.insert_one(
                    database = 'deribit',
                    collection = 'order_book_test',
                    document = order_book.model_dump()
                )
            )

        return True

    async def close(self) -> None:
        await self.grafana_connector.close()
        await self.mongo_connector.close()
        logger.info(f"{self} is closed.")