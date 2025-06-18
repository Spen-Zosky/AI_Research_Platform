from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .project import Base
import enum

class EntityType(enum.Enum):
    PERSON = "PER"
    ORGANIZATION = "ORG"
    LOCATION = "LOC"
    GEOPOLITICAL = "GPE"

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    label = Column(Enum(EntityType))
    source_id = Column(Integer, ForeignKey('sources.id'))
    source = relationship("Source", back_populates="entities")
