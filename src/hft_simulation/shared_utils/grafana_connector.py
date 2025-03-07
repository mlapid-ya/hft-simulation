from __future__ import annotations

import os

from loguru import logger
from dotenv import load_dotenv
import websockets.asyncio.client
from websockets.asyncio.client import ClientConnection

from hft_simulation.shared_utils.grafana_metric import GrafanaMetric

load_dotenv()

class GrafanaConnector:
    def __init__(self, stream_name: str):
        self.stream_name = stream_name

        self._websocket: ClientConnection | None = None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(stream_name={self.stream_name})"

    async def connect(self) -> None:
        api_key = os.getenv('GRAFANA_API_KEY')
        if not api_key:
            logger.error("GRAFANA_API_KEY is not set in the environment.")
            return
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        try:
            self._websocket: ClientConnection = await websockets.asyncio.client.connect(
                uri=f"ws://localhost:3000/api/live/push/{self.stream_name}",
                additional_headers=headers
            )
        except Exception as e:
            logger.error(f"Failed to connect to Grafana WebSocket: {e}")
            raise e
        
        logger.info(f"{self} is connected.")

    async def close(self) -> None:
        if self._websocket is not None:
            await self._websocket.close()
            logger.info(f"{self} is closed.")
        else:
            logger.error(f"{self} is not connected.")

    async def send(self, channel_name: str, data: dict[str, int | float], timestamp: float) -> None:
        if self._websocket is None:
            logger.error(f"{self} is not connected.")
            return

        metric = GrafanaMetric(
            stream_name=self.stream_name,
            channel_name=channel_name,
            data=data,
            timestamp=timestamp
        )

        await self._websocket.send(metric.line_protocol)
