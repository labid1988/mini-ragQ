from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class ProcessRequest(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") 
    file_id:str = None
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0

    model_config = {
        "arbitrary_types_allowed": True  # ✅ Pydantic v2
    }