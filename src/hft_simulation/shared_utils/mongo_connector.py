import os

from loguru import logger
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

load_dotenv(override=True)

class MongoConnector:

    def __init__(self):

        self.client: AsyncMongoClient = AsyncMongoClient(
            os.getenv('MONGO_URI'),
            username=os.getenv('MONGO_USER'),
            password=os.getenv('MONGO_PASSWORD')
        )

    async def connect(self) -> None:
        try:
            await self.client.aconnect()
        except Exception as e:
            logger.error(f"{self} failed to connect to MongoDB: {e}")
            raise e
        
        logger.info(f"{self} is connected.")

    def __str__(self):
        return f"{self.__class__.__name__}(host={self.client.host}, port={self.client.port})"
    
    def __repr__(self):
        return self.__str__()

    async def close(self) -> None:
        await self.client.close()
        logger.info(f"{self} is closed.")

    async def insert_one(self, database: str, collection: str, document: dict) -> None:
        await self.client[database][collection].insert_one(document)