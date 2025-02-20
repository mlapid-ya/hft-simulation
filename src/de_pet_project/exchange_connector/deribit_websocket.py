import json
import time
import asyncio
from datetime import datetime

import websockets.asyncio.client
from websockets.asyncio.client import ClientConnection
from loguru import logger
from dotenv import load_dotenv

from de_pet_project.exchange_connector.utils.offset import calculate_offset
from de_pet_project.exchange_connector.websocket_manager import WebsocketManager
from de_pet_project.exchange_connector.message_processor import MessageProcessor

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

        self.message_processor: MessageProcessor = MessageProcessor(stream_name=self.stream_name)

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

    async def __ainit__(self) -> None:
        logger.info("Starting")

        try:
            await self.message_processor.__ainit__()
        except Exception as e:
            logger.error(f"Failed to start: {e}")
            raise e
        
        try:
            self.websocket: ClientConnection = await websockets.asyncio.client.connect(
                uri=URL
            )
        except Exception as e:
            logger.error(f"Failed to connect to Deribit WebSocket: {e}")
            raise e
        
        logger.info(f"Connected to Deribit WebSocket")
        self.connected = True

        try: 
            #await asyncio.sleep(3600)
            async with asyncio.TaskGroup() as deribit_group:
                deribit_group.create_task(self.subscribe())
                deribit_group.create_task(self.receive())
        except asyncio.CancelledError:
            logger.info("Deribit websocket task cancelled")
            await self.close()

    async def close(self) -> None:
        await self.websocket.close()
        await self.message_processor.close()
        self.connected = False
        logger.info(f"Connection to Deribit WebSocket closed")

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

    async def send(self, message: dict) -> None:
        if self.connected:
            self.round_trip_data['client_send'] = time.time()
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent {message} to Deribit WebSocket")
        else:
            logger.error(f"Not connected to Deribit WebSocket")
    
    async def receive(self) -> None:
        while self.connected:
            try:
                response: str = await self.websocket.recv()
                ts_received: float = time.time()

                message: dict = json.loads(response)

                if 'id' in message:

                    logger.info(f"Received initial message: {message}")

                    self.round_trip_data['client_recv'] = ts_received + self.offset
                    self.round_trip_data['server_recv'] = message['usIn'] / 1e6
                    self.round_trip_data['server_send'] = message['usOut'] / 1e6
                    self.offset = calculate_offset(
                        self.round_trip_data['client_send'],
                        self.round_trip_data['server_recv'],
                        self.round_trip_data['server_send'],
                        self.round_trip_data['client_recv']
                    )

                    self.print_round_trip_data()

                    logger.info(f"Offset set to: {self.offset}")
                    # TODO: Recalculate offset periodically
                    continue

                if 'params' in message:
                    # logger.info(f"Received message: {message}")
                    await self.message_processor.process_message(
                        {
                            'ts_received': ts_received,
                            'offset': self.offset,
                            'channel': message['params']['channel'],
                            'data': message['params']['data'],
                        }
                    )

            except websockets.ConnectionClosed as e:
                logger.error(f"Connection closed: {e}")
                self.connected = False
            except Exception as e:
                logger.error(f"Error receiving message: {e}")