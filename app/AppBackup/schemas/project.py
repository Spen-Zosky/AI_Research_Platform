from pydantic import BaseModel, ConfigDict
import datetime
from typing import Optional, List

# Importa lo schema Source per la relazione
from .source import Source 

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Lo schema di lettura ora includerà una lista di fonti
class Project(ProjectBase):
    id: int
    created_at: datetime.datetime
    sources: List[Source] = []

    model_config = ConfigDict(from_attributes=True)
