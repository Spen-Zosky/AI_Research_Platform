from pydantic import BaseModel, ConfigDict
import datetime
from typing import Optional, List
from .entity import Entity # Importa lo schema Entity

class SourceBase(BaseModel):
    title: str
    url: Optional[str] = None
    content: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    content: str

class Source(SourceBase):
    id: int
    project_id: int
    created_at: datetime.datetime
    entities: List[Entity] = [] # Aggiunge la lista di entità
    model_config = ConfigDict(from_attributes=True)
