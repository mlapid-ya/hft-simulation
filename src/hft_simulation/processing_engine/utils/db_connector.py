import asyncio

import aiosqlite

from loguru import logger

class DBConnector:

    def __init__(self, db_path: str):
        self.db_path: str = db_path

        self.db: aiosqlite.Connection = None

    async def __ainit__(self) -> None:
        try:
            self.db = await aiosqlite.connect(self.db_path)
        except Exception as e:
            logger.error(f"Failed to connect to {self.db_path}: {e}")
            raise e
        else:
            logger.info(f"{self} is initialized.")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(db_path={self.db_path})"

    async def close(self) -> None:
        await self.db.close()
        logger.info(f"{self} is closed.")
        
    async def create_table(self, table_name: str, table_schema: dict[str, str]) -> None:
        
        columns: list[str] = [f"{col_name} {col_type}" for col_name, col_type in table_schema.items()]

        async with self.db.cursor() as cursor:
            await cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            await cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            )
            await self.db.commit()
            logger.info(f"Table {table_name} with schema {table_schema} created.")
        

async def test_db_connector():
    db_connector = DBConnector(db_path="order_book.db")
    await db_connector.__ainit__()
    async with db_connector.db.cursor() as cursor:
        await db_connector.create_table(
            table_name="test",
            table_schema={
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "ts_received": "INTEGER",
                "price": "REAL",
                "volume": "REAL"
            }
        )
        await cursor.execute(
            '''
            INSERT INTO test (ts_received, price, volume)
            VALUES (?, ?, ?)
            ''',
            (1, 100, 10)
        )
        await db_connector.db.commit()
        await cursor.execute(
            '''
            SELECT * FROM test
            '''
        )
        print(await cursor.fetchall())
    await db_connector.close()

if __name__ == "__main__":
    asyncio.run(test_db_connector())
        