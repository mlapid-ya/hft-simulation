import time
import asyncio
import aiosqlite
from itertools import chain

from loguru import logger

from de_pet_project.shared_utils.message_processor import MessageProcessor
from de_pet_project.shared_utils.grafana_connector import GrafanaConnector
# from de_pet_project.processing_engine.utils.db_connector import DBConnector
from de_pet_project.shared_utils.order_book import OrderBook
# from de_pet_project.processing_engine.utils.table_schema import table_schema

class StreamProcessor(MessageProcessor):

    def __init__(self, stream_name: str):
        super().__init__(stream_name=stream_name)

        self.grafana_connector = GrafanaConnector(stream_name=self.stream_name)
        # self.db_connector = DBConnector(db_path='data/order_book.db')

        self.counter: int = 0

    async def __ainit__(self) -> None:
        try:
            await self.grafana_connector.__ainit__()
            # await self.db_connector.__ainit__()

            # await self.db_connector.create_table(
            #     table_name='bids',
            #     table_schema=table_schema
            # )
            # await self.db_connector.create_table(
            #     table_name='asks',
            #     table_schema=table_schema
            # )
        except Exception as e:
            logger.error(f"Failed to initialize {self}: {e}")
            raise e
        else:
            logger.info(f"{self} is initialized.")
    
    async def process_message(self, message: dict) -> None:
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

        await self.grafana_connector.send(
            channel_name = 'processing_engine',
            data = {
                'delta_message_processed': ts_received - message['ts_sent'],
            },
            timestamp = ts_received
        )

        await self.grafana_connector.send(
            channel_name = 'order_book',
            data = {
                'microprice': order_book.microprice,
                'imbalance': order_book.total_volume_imbalance,
                'spread': order_book.spread,
            },
            timestamp = order_book.timestamp
        )

        # async with asyncio.TaskGroup() as tg:
        #     tg.create_task(self.send_to_grafana(order_book))
        #     tg.create_task(self.send_to_db(order_book))

    async def send_to_grafana(self, order_book: OrderBook) -> None:
        pass

    # async def send_to_db(self, order_book: OrderBook) -> None:
    #     async with asyncio.Semaphore(1): # Ensure that only one task is writing to the database at a time
    #         async with self.db_connector.db.cursor() as cursor:
    #             await cursor.execute(
    #                 '''
    #                 INSERT INTO bids (ts_received, price_1, volume_1, price_2, volume_2, price_3, volume_3, price_4, volume_4, price_5, volume_5, price_6, volume_6, price_7, volume_7, price_8, volume_8, price_9, volume_9, price_10, volume_10)
    #                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    #                 ''',
    #                 [order_book.timestamp] + list(chain.from_iterable(order_book.bids))
    #             )

    #             await cursor.execute(
    #                 '''
    #                 INSERT INTO asks (ts_received, price_1, volume_1, price_2, volume_2, price_3, volume_3, price_4, volume_4, price_5, volume_5, price_6, volume_6, price_7, volume_7, price_8, volume_8, price_9, volume_9, price_10, volume_10)
    #                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    #                 ''',
    #                 [order_book.timestamp] + list(chain.from_iterable(order_book.asks))
    #             )

    #             if self.counter % 1000 == 0:
    #                 await self.db_connector.db.commit()
    #                 logger.info(f"DB committed. Counter: {self.counter}")


    async def close(self) -> None:
        await self.grafana_connector.close()
        # await self.db_connector.close()
        logger.info(f"{self} is closed.")