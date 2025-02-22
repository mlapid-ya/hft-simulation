import json
import time
import asyncio
from datetime import datetime

from loguru import logger
from dotenv import load_dotenv
import websockets.asyncio.client
from websockets.asyncio.client import ClientConnection

from de_pet_project.exchange_connector.utils.offset import calculate_offset
from de_pet_project.exchange_connector.websocket_manager import WebsocketManager
from de_pet_project.exchange_connector.websocket_processor import WebsocketProcessor

load_dotenv()

#URL: str = "wss://test.deribit.com/ws/api/v2"
URL: str = "wss://www.deribit.com/ws/api/v2"

class DeribitWebsocket(WebsocketManager):

    stream_name: str = 'deribit_connector'

    def __init__(self):

        self.websocket: ClientConnection = None
        self.connected: bool = False

        self.round_trip_data: dict = {
            'client_send': 0,
            'server_recv': 0,
            'server_send': 0,
            'client_recv': 0
        }
        self.offset: float = 0

        self.message_processor: WebsocketProcessor = WebsocketProcessor(stream_name=self.stream_name)

    async def __ainit__(self) -> None:
        try:
            self.websocket: ClientConnection = await self._connect()
            await self.message_processor.__ainit__()
        except Exception as e:
            logger.error(f"Failed to initialize {self}: {e}")
            raise e
        
        async with asyncio.TaskGroup() as deribit_group:
            deribit_group.create_task(self.subscribe())
            deribit_group.create_task(self.receive())
            deribit_group.create_task(self.ping())

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(stream_name={self.stream_name})"

    async def _connect(self) -> ClientConnection:
        try:
            websocket_client: ClientConnection = await websockets.asyncio.client.connect(
                uri=URL
            )
        except Exception as e:
            logger.error(f"Failed to connect to Deribit WebSocket: {e}")
            raise e
        else:
            logger.info(f"{self} is connected")
            self.connected = True
            return websocket_client

    def print_round_trip_data(self) -> None:

        time_format: str = "%Y-%m-%d %H:%M:%S.%f"

        logger.info(
            f'''
            Round trip data:
            client_send: {datetime.fromtimestamp(self.round_trip_data["client_send"]).strftime(time_format)}
            server_recv: {datetime.fromtimestamp(self.round_trip_data["server_recv"]).strftime(time_format)}
            server_send: {datetime.fromtimestamp(self.round_trip_data['server_send']).strftime(time_format)}
            client_recv: {datetime.fromtimestamp(self.round_trip_data['client_recv']).strftime(time_format)}
            '''
        )

    async def close(self) -> None:
        await self.websocket.close()
        await self.message_processor.close()
        self.connected = False
        logger.info(f"{self} is closed")

    async def subscribe(self) -> None:

        channels = [
            "book.ETH-PERPETUAL.none.10.100ms"
        ]

        msg = {
            "jsonrpc" : "2.0",
            "id" : 3600,
            "method" : "public/subscribe",
            "params" : {
                    "channels" : channels
                }
            }
        
        await self.send(msg)
        logger.info(f"Subscribed to channel(s): {channels}")

    async def ping(self) -> None:
        
        msg = {
        "jsonrpc" : "2.0",
        "id" : 9098,
        "method" : "public/set_heartbeat",
            "params" : {
                "interval" : 10
            }
        }

        await self.send(msg)

    async def send(self, message: dict) -> None:
        if self.connected:
            await self.websocket.send(json.dumps(message))
            self.round_trip_data['client_send'] = time.time()
            logger.info(f"Sent {message} to {self}")
        else:
            logger.error(f"Not connected to {self}")
    
    async def receive(self) -> None:
        while self.connected:
            try:
                response: str = await self.websocket.recv()
                ts_received: float = time.time()
                # logger.info(f"Received message: {response}")

                message: dict = json.loads(response)

                if 'id' in message:
                    self.round_trip_data['server_recv'] = message['usIn'] / 1e6
                    self.round_trip_data['server_send'] = message['usOut'] / 1e6
                    self.round_trip_data['client_recv'] = ts_received

                    self.offset = calculate_offset(
                        self.round_trip_data['client_send'],
                        self.round_trip_data['server_recv'],
                        self.round_trip_data['server_send'],
                        self.round_trip_data['client_recv']
                    )

                    logger.info(f"Offset: {self.offset}")

                if 'method' in message:
                    if message['method'] == "heartbeat":
                        await self.ping()
                    elif message['method'] == "subscription":
                        logger.info(f"Received message: {message}")

                        await self.message_processor.process_message(
                            {
                                'ts_received': ts_received,
                                'offset': self.offset,
                                'channel': message['params']['channel'],
                                'data': message['params']['data'],
                            }
                        )
                    else:
                        logger.error(f"Received unknown message: {message}")

            except websockets.ConnectionClosed as e:
                logger.error(f"Connection closed: {e}")
                self.connected = False
            except Exception as e:
                logger.error(f"Error receiving message: {e}")