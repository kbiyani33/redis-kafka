import json
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.encoders import jsonable_encoder
from pymongo.errors import DuplicateKeyError
from models.item import ItemModel
from utils.db import mongo_client
from utils.kafka_utils import get_kafka_producer
from utils.redis_utils import get_from_cache, set_to_cache, invalidate_cache
from utils.decorators import log_api_endpoint_execution_time

router = APIRouter()
producer = get_kafka_producer()

@router.post("/items")
@log_api_endpoint_execution_time
async def create_item(request: Request, item: ItemModel):
    try:
        item_dict = jsonable_encoder(item)
        await mongo_client.client.fastapi_db.items.insert_one(item_dict)
        
        # Kafka and Redis
        producer.send("crud_operations", {"operation": "create", "item": item_dict})
        invalidate_cache(str(item.id))
        
        return {"message": "Item created successfully", "item": item_dict}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Item already exists")

@router.get("/items/{item_id}")
@log_api_endpoint_execution_time
async def read_item(request:Request, item_id: str):
    cached_item = get_from_cache(item_id)
    if cached_item:
        return {"item": json.loads(cached_item), "source": "cache"}
    
    item = await mongo_client.client.fastapi_db.items.find_one({"_id": str(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    set_to_cache(item_id, item)
    return {"item": item, "source": "database"}

@router.put("/items/{item_id}")
@log_api_endpoint_execution_time
async def update_item(request:Request, item_id: str, item: ItemModel):
    result = await  mongo_client.client.fastapi_db.items.update_one({"_id": str(item_id)}, {"$set": item.dict(by_alias=True)})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    producer.send("crud_operations", {"operation": "update", "item_id": item_id, "data": item.dict(by_alias=True)})
    invalidate_cache(item_id)
    return {"message": "Item updated successfully", "item": item.dict(by_alias=True)}

@router.delete("/items/{item_id}")
@log_api_endpoint_execution_time
async def delete_item(request:Request, item_id: str):
    result = await mongo_client.client.fastapi_db.items.delete_one({"_id": str(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    producer.send("crud_operations", {"operation": "delete", "item_id": item_id})
    invalidate_cache(item_id)
    return {"message": "Item deleted successfully"}
