from typing import Annotated
from datetime import datetime
from collections import namedtuple

from loguru import logger
from pydantic.config import ConfigDict
from pydantic import BaseModel, Field, field_validator

Level = namedtuple('Level', ['price', 'volume'])

class OrderBook(BaseModel):
    model_config = ConfigDict(
        title='OrderBook',
        frozen=True,
        arbitrary_types_allowed=True
    )

    timestamp:       Annotated[datetime, Field(alias='timestamp')]
    instrument_name: Annotated[str, Field(alias='instrument_name')]
    bids:            Annotated[list[Level[float, float]], Field(alias='bids')]
    asks:            Annotated[list[Level[float, float]], Field(alias='asks')]

    def model_post_init(self, __context):
        if len(self.bids) != len(self.asks):
           logger.error(f'Number of bids and asks must be equal, got {len(self.bids)} != {len(self.asks)}')

    @field_validator('timestamp', mode='before')
    def convert_timestamp_to_datetime(cls, timestamp: float | datetime | str) -> datetime:
        if isinstance(timestamp, float):
            return datetime.fromtimestamp(timestamp, tz=None)
        elif isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp)
        else:
            raise ValueError(f'Invalid timestamp: {timestamp}')

    @field_validator('bids', mode='before')
    def convert_bids_to_levels(cls, v: list[list[float, float]]) -> list[Level[float, float]]:
        return [Level(price=v[0], volume=v[1]) for v in v]

    @field_validator('asks', mode='before')
    def convert_asks_to_levels(cls, v: list[list[float, float]]) -> list[Level[float, float]]:
        return [Level(price=v[0], volume=v[1]) for v in v]


    @field_validator('bids', mode='after')
    def validate_bids(cls, v: list[Level[float, float]]) -> list[Level[float, float]]:
        for i in range(len(v) - 1):
            if v[i].price < v[i + 1].price:
                logger.error(f'Bids are not sorted: {v[i].price} < {v[i + 1].price}')
        return v

    @field_validator('asks', mode='after')
    def validate_asks(cls, v: list[Level[float, float]]) -> list[Level[float, float]]:
        for i in range(len(v) - 1):
            if v[i].price > v[i + 1].price:
                logger.error(f'Asks are not sorted: {v[i].price} > {v[i + 1].price}')
        return v
    
    @property
    def bid_price(self) -> float:
        return self.bids[0].price
    
    @property
    def bid_volume(self) -> float:
        return self.bids[0].volume
    
    @property
    def ask_price(self) -> float:
        return self.asks[0].price
    
    @property
    def ask_volume(self) -> float:
        return self.asks[0].volume

    @property
    def mid_price(self) -> float:
        return (self.bid_price + self.ask_price) / 2
    
    @property
    def micro_price(self) -> float:
        return ( (self.ask_price * self.bid_volume) + (self.bid_price * self.ask_volume) ) / (self.bid_volume + self.ask_volume)
    
    @property
    def spread(self) -> float:
        return round(self.ask_price - self.bid_price, 4)
    
    @property
    def bid_volume_total(self) -> float:
        return sum(level.volume for level in self.bids)
    
    @property
    def ask_volume_total(self) -> float:
        return sum(level.volume for level in self.asks)
    
    @property
    def volume_imbalance(self) -> float:
        return (self.bid_volume - self.ask_volume) / (self.bid_volume + self.ask_volume)
    
    @property
    def volume_imbalance_total(self) -> float:
        return (self.bid_volume_total - self.ask_volume_total) / (self.bid_volume_total + self.ask_volume_total)
    
    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
            f'timestamp={self.timestamp}, ' \
            f'instrument_name={self.instrument_name}, ' \
            f'bid_price={self.bid_price}, ' \
            f'ask_price={self.ask_price}, ' \
            f'mid_price={self.mid_price}, ' \
            f'spread={self.spread}, ' \
            f'volume_imbalance={self.volume_imbalance} , ' \
            f'volume_imbalance_total={self.volume_imbalance_total})'

    def __repr__(self) -> str:
        return self.__str__()

    def get_volume_imbalance(self, lvl: int) -> float:
        if not (1 <= lvl <= self.depth):
            # logger.error(f"Level must be between 1 and {self.depth}, got {lvl}")
            raise ValueError(f"Level must be between 1 and {self.depth}, got {lvl}")
        
        bid_volume: float = self.bids[lvl - 1].volume
        ask_volume: float = self.asks[lvl - 1].volume
        return (bid_volume - ask_volume) / (bid_volume + ask_volume)
