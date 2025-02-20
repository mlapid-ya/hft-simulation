import pytest
import pytest_asyncio

from de_pet_project.exchange_connector.utils.redis_producer import RedisProducer

class TestRedisProducer:

    stream_name: str = "test"

    @pytest_asyncio.fixture(scope="session")
    async def redis_producer(self):
        producer = RedisProducer(self.stream_name)
        await producer.__ainit__()
        yield producer
        await producer.close()

    @pytest.mark.asyncio
    async def test_stream_length(self, redis_producer):
        await redis_producer.produce_message("Hello, World!")
        assert redis_producer.stream_length == 1
