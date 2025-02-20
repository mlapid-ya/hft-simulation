import redis

from loguru import logger

from de_pet_project.shared_utils.redis_client import RedisClient

class RedisProducer(RedisClient):
    '''
    Redis producer
    '''

    def __init__(self, stream_name: str):
        super().__init__(stream_name)

    def produce_message(self, message: str) -> None:
        try:
            self._redis_client.xadd(name=self.stream_name, fields={'message': message})
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")
            raise e

    def close(self) -> None:
        self._redis_client.flushall()
        self._redis_client.close()
        logger.info(f"{self} is closed.")