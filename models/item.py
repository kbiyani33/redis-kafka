from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

from pydantic import BaseModel, field_validator
from bson import ObjectId
from typing import Any
import uuid

# Custom type for ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: dict, field_info: Any) -> dict:
        """
        This method is called in Pydantic v2 to modify the schema for custom types.
        We return the schema for the ObjectId type.
        """
        field_schema.update({"type": "string", "format": "object-id"})
        return field_schema

    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        """Validate and convert a value to ObjectId."""
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            try:
                return ObjectId(v)
            except Exception:
                raise ValueError("Invalid ObjectId format")
        raise ValueError("Invalid ObjectId format")


class ItemModel(BaseModel):
    id: PyObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    name: str
    description: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Sample Item",
                "description": "This is a sample item",
            }
        }
