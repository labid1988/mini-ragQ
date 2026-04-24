# from pydantic import BaseModel, Field, validator
# from typing import Optional
# from bson.objectid import ObjectId

# class Project(BaseModel):
#     _id: Optional[ObjectId]
#     project_id: str = Field(..., min_length=1)

# @validator('project_id')
# def validate_project_id(cls, value):
#     if not value.isalnum():
#         raise ValueError('project_id must be alphanumeric')
#     return value

# class Config:
#     arbitrary_types_allowed = True

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    #id: Optional[ObjectId] = None        # ✅ _id → id (Pydantic v2)
    project_id: str = Field(..., min_length=1)

    @field_validator('project_id')       # ✅ indenté dans la classe
    @classmethod                         # ✅ requis en Pydantic v2
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        return value

    # class Config:                        
    #     arbitrary_types_allowed = True

    model_config = {
    "arbitrary_types_allowed": True,
    "populate_by_name": True  # permet d'utiliser "id" ou "_id"
}


    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("project_id", 1)
                ],
                "name":"project_id_index_1",
                "unique": True
            }
        ]