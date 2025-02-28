from typing import Annotated, Literal
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

class Trade(BaseModel):
    timestamp: Annotated[datetime, Field(alias='timestamp')]
    instrument_name: Annotated[str, Field(alias='instrument_name')]
    action: Annotated[Literal['BUY', 'SELL'], Field(alias='action')]
    price: Annotated[float, Field(alias='price')]
    size: Annotated[float, Field(alias='size')]

    @field_validator('timestamp', mode='before')
    def convert_timestamp_to_datetime(cls, timestamp: float | datetime | str) -> datetime:
        if isinstance(timestamp, float):
            return datetime.fromtimestamp(timestamp, tz=None)
        elif isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp)
        else:
            raise ValueError(f"Invalid timestamp: {timestamp}")

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
            f'timestamp={self.timestamp}, ' \
            f'instrument_name={self.instrument_name}, ' \
            f'action={self.action}, ' \
            f'price={self.price}, ' \
            f'size={self.size})'

    def __repr__(self) -> str:
        return self.__str__()