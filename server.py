from typing import AsyncGenerator
import logging
from fastapi import FastAPI
from utils.db import mongo_client
from routes.crud_with_kafka_redis import router as crud_router
from routes.crud_with_kafka_without_redis import router as crud_with_kafka_without_redis

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Code to run on startup
    logger.info("Starting the application...")
    await mongo_client.connect_to_mongo()  # Connect to MongoDB
    # Yield control back to the application during runtime
    yield
    # Code to run on shutdown
    logger.info("Shutting down the application...")
    await mongo_client.close_mongo_connection()  # Close MongoDB connection

app = FastAPI(lifespan=lifespan)  # Pass the lifespan function
app.include_router(crud_router, prefix="/api")
app.include_router(crud_with_kafka_without_redis, prefix="/api/kafka-only")

# Define some simple routes to test the app
@app.get("/")
async def root():
    return {"message": "Hello World!"}