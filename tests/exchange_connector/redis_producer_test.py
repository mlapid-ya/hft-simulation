import pytest
import pytest_asyncio

from hft_simulation.exchange_connector.utils.redis_producer import RedisProducer

class TestRedisProducer:

    stream_name: str = "test"

    @pytest_asyncio.fixture(scope="function")
    async def redis_producer(self):
        producer = RedisProducer(self.stream_name)
        await producer.__ainit__()
        yield producer
        await producer.close()

    @pytest.mark.asyncio
    async def test_stream_length(self, redis_producer):
        await redis_producer.produce_message("Hello, World!")
        stream_length: int = await redis_producer.stream_length()
        assert stream_length == 1
