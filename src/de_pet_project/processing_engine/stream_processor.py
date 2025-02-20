from loguru import logger

from de_pet_project.shared_utils.message_processor import MessageProcessor
from de_pet_project.shared_utils.grafana_connector import GrafanaConnector
from de_pet_project.shared_utils.order_book import OrderBook

class StreamProcessor(MessageProcessor):

    def __init__(self, stream_name: str):
        super().__init__(stream_name=stream_name)

        self.grafana_connector = GrafanaConnector(stream_name=self.stream_name)

    async def __ainit__(self) -> None:
        try:
            await self.grafana_connector.__ainit__()
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
        logger.info(f"Message received: {message}")

        order_book: OrderBook = OrderBook(**message['data'])

        await self.grafana_connector.send(
            channel_name='processing_engine',
            data={
                'microprice': order_book.microprice,
                'imbalance': order_book.total_volume_imbalance,
                'spread': order_book.spread,
            },
            timestamp=order_book.timestamp
        )

    async def close(self) -> None:
        await self.grafana_connector.close()
        logger.info(f"{self} is closed.")
