from typing import Annotated
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

    timestamp:       Annotated[float, Field(alias='timestamp')]
    change_id:       Annotated[int, Field(alias='change_id')]
    instrument_name: Annotated[str, Field(alias='instrument_name')]
    bids:            Annotated[list[Level[float, float]], Field(alias='bids')]
    asks:            Annotated[list[Level[float, float]], Field(alias='asks')]

    def model_post_init(self, __context):
        if len(self.bids) != len(self.asks):
           logger.error(f"Number of bids and asks must be equal, got {len(self.bids)} != {len(self.asks)}")

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
                logger.error(f"Bids are not sorted: {v[i].price} < {v[i + 1].price}")
        return v

    @field_validator('asks', mode='after')
    def validate_asks(cls, v: list[Level[float, float]]) -> list[Level[float, float]]:
        for i in range(len(v) - 1):
            if v[i].price > v[i + 1].price:
                logger.error(f"Asks are not sorted: {v[i].price} > {v[i + 1].price}")
        return v

    @property
    def midprice(self) -> float:
        return (self.bids[0].price + self.asks[0].price) / 2
    
    @property
    def microprice(self) -> float:
        return ( (self.asks[0].price * self.bids[0].volume) + (self.bids[0].price * self.asks[0].volume) ) / (self.bids[0].volume + self.asks[0].volume)
    
    @property
    def spread(self) -> float:
        return self.asks[0].price - self.bids[0].price
    
    @property
    def total_bid_volume(self) -> float:
        return sum(volume for price, volume in self.bids)
    
    @property
    def total_ask_volume(self) -> float:
        return sum(volume for price, volume in self.asks)
    
    @property
    def total_volume_imbalance(self) -> float:
        return (self.total_bid_volume - self.total_ask_volume) / (self.total_bid_volume + self.total_ask_volume)

    def get_volume_imbalance(self, lvl: int) -> float:
        if not (1 <= lvl <= self.depth):
            # logger.error(f"Level must be between 1 and {self.depth}, got {lvl}")
            raise ValueError(f"Level must be between 1 and {self.depth}, got {lvl}")
        
        bid_volume: float = self.bids[lvl - 1][1]
        ask_volume: float = self.asks[lvl - 1][1]
        return (bid_volume - ask_volume) / (bid_volume + ask_volume)
