from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator

class GrafanaMetric(BaseModel):
    stream_name:  Annotated[str, Field(alias='stream_name')]
    channel_name: Annotated[str, Field(alias='channel_name')]
    data:         Annotated[dict[str, Optional[int | float]], Field(alias='data')]
    timestamp:    Annotated[int, Field(alias='timestamp')]

    @field_validator('timestamp', mode='before')
    def validate_timestamp(cls, value):
        return int(value * 1e9)

    @property
    def data_str(self) -> str:
        return ','.join(f"{key}={value}" for key, value in self.data.items())

    @property
    def line_protocol(self) -> str:
        return f'{self.channel_name},stream={self.stream_name} {self.data_str} {self.timestamp}'