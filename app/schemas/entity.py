from pydantic import BaseModel, ConfigDict
from typing import Optional

class EntityBase(BaseModel):
    text: str
    label: str

class EntityCreate(EntityBase):
    pass

class Entity(EntityBase):
    id: int
    source_id: int
    model_config = ConfigDict(from_attributes=True)
