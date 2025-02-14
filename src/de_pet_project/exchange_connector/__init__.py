import asyncio

from loguru import logger

from de_pet_project.exchange_connector.deribit_websocket import DeribitWebsocket

async def run():

    deribit_websocket = DeribitWebsocket()

    start_websocket_task = asyncio.create_task(deribit_websocket.__ainit__()) 

    try:
        await start_websocket_task
    except Exception as e:
        logger.error(f"Failed to start: {e}")

def main():
    asyncio.run(run())