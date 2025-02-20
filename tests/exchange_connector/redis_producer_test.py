import pytest

from de_pet_project.exchange_connector.utils.redis_producer import RedisProducer

class TestRedisProducer:

    stream_name: str = "test"

    @pytest.fixture(scope="function")
    def redis_producer(self):
        producer = RedisProducer(self.stream_name)
        yield producer
        producer.close()

    def test_stream_length(self, redis_producer):
        redis_producer.produce_message("Hello, World!")
        assert redis_producer.stream_length == 1
