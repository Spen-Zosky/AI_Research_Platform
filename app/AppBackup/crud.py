from sqlalchemy.orm import Session
from sqlalchemy import func

# Importa i modelli e gli schemi usando alias per chiarezza
from .models import project as project_model, source as source_model, entity as entity_model
from .schemas import project as project_schema, source as source_schema, entity as entity_schema

# --- CRUD per i Progetti ---

def get_project(db: Session, project_id: int):
    return db.query(project_model.Project).filter(project_model.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(project_model.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: project_schema.ProjectCreate):
    db_project = project_model.Project(name=project.name, description=project.description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project_update: project_schema.ProjectUpdate):
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    update_data = project_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project

# --- CRUD per le Fonti ---

def get_source(db: Session, source_id: int):
    return db.query(source_model.Source).filter(source_model.Source.id == source_id).first()

def get_sources_for_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(source_model.Source).filter(source_model.Source.project_id == project_id).offset(skip).limit(limit).all()

def create_project_source(db: Session, source: source_schema.SourceCreate, project_id: int):
    db_source = source_model.Source(**source.dict(), project_id=project_id)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

def update_source_content(db: Session, source_id: int, content: str):
    db_source = get_source(db, source_id=source_id)
    if not db_source:
        return None
    db_source.content = content
    db.commit()
    db.refresh(db_source)
    return db_source

# --- Funzione di Ricerca ---

def search_sources_content(db: Session, query: str, skip: int = 0, limit: int = 100):
    search_query = func.websearch_to_tsquery('italian', query)
    return db.query(source_model.Source).filter(
        source_model.Source.content.isnot(None),
        func.to_tsvector('italian', source_model.Source.content).op('@@')(search_query)
    ).offset(skip).limit(limit).all()

# --- Funzioni CRUD per le Entità ---

def create_source_entity(db: Session, entity: entity_schema.EntityCreate, source_id: int):
    existing_entity = db.query(entity_model.Entity).filter_by(text=entity.text, label=entity.label, source_id=source_id).first()
    if existing_entity:
        return existing_entity
    db_entity = entity_model.Entity(**entity.dict(), source_id=source_id)
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity
