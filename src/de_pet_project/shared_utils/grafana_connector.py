from __future__ import annotations

import os
import time
from typing import Optional, Annotated

import websockets.asyncio.client
from websockets.asyncio.client import ClientConnection
from loguru import logger
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()

class GrafanaConnector:
    def __init__(self, stream_name: str):
        self.stream_name = stream_name

        self._websocket: ClientConnection = None

    async def __ainit__(self) -> None:
        self._websocket = await self._connect()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(stream_name={self.stream_name})"

    async def _connect(self) -> ClientConnection:
        
        headers = {
            "Authorization": f"Bearer {os.getenv('GRAFANA_API_KEY')}"
        }

        try:
            websocket_client: ClientConnection = await websockets.asyncio.client.connect(
                uri=f"ws://localhost:3000/api/live/push/{self.stream_name}",
                additional_headers=headers
            )
        except Exception as e:
            logger.error(f"Failed to connect to Grafana WebSocket: {e}")
            raise e
        else:
            logger.info(f"{self} is connected.")
            return websocket_client

    async def close(self) -> None:
        await self._websocket.close()
        logger.info(f"{self} is closed.")

    async def send(self, channel_name: str, data: dict[str, Optional[int | float]], timestamp: float) -> None:

        metric = GrafanaMetric(
            stream_name=self.stream_name,
            channel_name=channel_name,
            data=data,
            timestamp=timestamp
        )

        await self._websocket.send(metric.line_protocol)


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