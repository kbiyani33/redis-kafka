from pymongo import AsyncMongoClient
from .constants import MONGODB_URI
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MongoDBClientInstance:
    def __init__(self, uri: str):
        self.uri = uri
        self.client: Optional[AsyncMongoClient] = None

    async def connect_to_mongo(self) -> None:
        if self.client is not None:
            logger.info("MongoDB client already connected.")
            return
        logger.info("Connecting to MongoDB...")
        self.client = AsyncMongoClient(self.uri)

    async def close_mongo_connection(self) -> None:
        if self.client is not None:
            logger.info("Closing MongoDB client connection...")
            await self.client.close()
            self.client = None

    def get_mongo_client_instance(self) -> AsyncMongoClient:
        if self.client is None:
            raise RuntimeError("No connection has been established.")
        return self.client

mongo_client = MongoDBClientInstance(MONGODB_URI)