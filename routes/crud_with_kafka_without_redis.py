from fastapi import APIRouter, HTTPException, Depends, Request
from pymongo.errors import DuplicateKeyError
from models.item import ItemModel
from utils.db import mongo_client
from utils.kafka_utils import get_kafka_producer
from utils.decorators import log_api_endpoint_execution_time

router = APIRouter()
producer = get_kafka_producer()

@router.post("/kafka-only/items")
@log_api_endpoint_execution_time
async def create_item(request:Request, item: ItemModel):
    try:
        item_dict = item.model_dump(mode="json", by_alias=True)
        await mongo_client.client.fastapi_db.items.insert_one(item_dict)
        
        # Kafka and no Redis
        producer.send("crud_operations", {"operation": "create", "item": item_dict})
        # invalidate_cache(str(item.id))
        
        return {"message": "Item created successfully", "item": item_dict}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Item already exists")

@router.get("/kafka-only/items/{item_id}")
@log_api_endpoint_execution_time
async def read_item(request:Request, item_id: str):
    item = await mongo_client.client.fastapi_db.items.find_one({"_id": str(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # set_to_cache(item_id, item)
    return {"item": item, "source": "database"}

@router.put("/kafka-only/items/{item_id}")
@log_api_endpoint_execution_time
async def update_item(request:Request, item_id: str, item: ItemModel):
    result = await mongo_client.client.fastapi_db.items.update_one({"_id": str(item_id)}, {"$set": item.dict(by_alias=True)})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    producer.send("crud_operations", {"operation": "update", "item_id": item_id, "data": item.dict(by_alias=True)})
    # invalidate_cache(item_id)
    return {"message": "Item updated successfully", "item": item.dict(by_alias=True)}

@router.delete("/kafka-only/items/{item_id}")
@log_api_endpoint_execution_time
async def delete_item(request:Request, item_id: str):
    result = await mongo_client.client.fastapi_db.items.delete_one({"_id": str(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    producer.send("crud_operations", {"operation": "delete", "item_id": item_id})
    # invalidate_cache(item_id)
    return {"message": "Item deleted successfully"}
