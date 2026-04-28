from pydantic import BaseModel, Field, validator
from bson.objectid import ObjectId
from typing import Optional

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict = Field(default_factory=dict)
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True
    


    @classmethod
    def get_indexes(cls):

        return [
            {
                "key":[
                    ("project_id", 1)
                ],
                "name":"project_id_index_1",
                "unique": False
            }
        ]