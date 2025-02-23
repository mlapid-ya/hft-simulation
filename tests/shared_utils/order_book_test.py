import pytest

from hft_simulation.shared_utils.order_book import OrderBook, Level

class TestOrderBook:

    @pytest.fixture(scope="function")
    def order_book(self):
        return OrderBook(
            timestamp=1739524537.4823868,
            change_id=1,
            instrument_name='ETH-PERPETUAL',
            bids=[[10000, 100], [10001, 100]],
            asks=[[10002, 100], [10003, 100]])
    
    def test_bids(self, order_book):
        assert order_book.bids == [Level(price=10000, volume=100), Level(price=10001, volume=100)]

    def test_asks(self, order_book):
        assert order_book.asks == [Level(price=10002, volume=100), Level(price=10003, volume=100)]

    def test_timestamp(self, order_book):
        assert order_book.timestamp == 1739524537.4823868