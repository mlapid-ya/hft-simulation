import asyncio

from loguru import logger

from de_pet_project.exchange_connector.deribit_websocket import DeribitWebsocket

async def run():

    deribit_websocket = DeribitWebsocket()

    try:
        async with asyncio.TaskGroup() as exchange_connector:
            exchange_connector.create_task(deribit_websocket.__ainit__())
    except asyncio.CancelledError:
        logger.info("Closing the exchange connector.")
        await deribit_websocket.close()

def main():
    asyncio.run(run())