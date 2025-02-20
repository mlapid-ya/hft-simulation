import os
from abc import ABC, abstractmethod

import redis
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class RedisClient(ABC):
    '''
    Abstract class for Redis producers and consumers
    '''

    def __init__(self, stream_name: str):
        self.stream_name: str = stream_name

        self._redis_client: redis.Redis = self._connect()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(stream_name={self.stream_name})"

    @property
    def stream_length(self) -> int:
        return self._redis_client.xlen(self.stream_name)
    
    @abstractmethod
    def close(self) -> None:
        pass

    def _connect(self) -> redis.Redis:
        '''
        Connect to Redis

        Use configuration from environment variables.
        '''

        host: str = os.getenv('REDIS_HOST')
        port: int = os.getenv('REDIS_PORT')
        db: int = os.getenv('REDIS_DB')

        try:
            redis_client: redis.Redis = redis.Redis(host=host, port=port, db=db)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise e
        else:
            logger.info(f"{self} is connected.")
            return redis_client