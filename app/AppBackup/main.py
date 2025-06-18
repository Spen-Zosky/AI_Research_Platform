import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .core.database import get_db
from . import crud
from .schemas import project as project_schema, source as source_schema

app = FastAPI(
    title="AI Augmented Research Platform",
    description="Backend API for the research platform",
    version="0.3.0"
)

# --- Endpoint per la RICERCA ---
@app.get("/search/", response_model=List[source_schema.Source], tags=["Search"])
def search_in_sources(q: str = Query(..., min_length=3), db: Session = Depends(get_db)):
    """
    Esegue una ricerca full-text nel contenuto di tutte le fonti.
    """
    results = crud.search_sources_content(db=db, query=q)
    return results

# --- Endpoints per PROGETTI ---
@app.post("/projects/", response_model=project_schema.Project, tags=["Projects"])
def create_project_endpoint(project: project_schema.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db=db, project=project)
# ... (gli altri endpoint per i progetti rimangono invariati) ...
@app.get("/projects/", response_model=List[project_schema.Project], tags=["Projects"])
def read_projects_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_projects(db, skip=skip, limit=limit)
@app.get("/projects/{project_id}", response_model=project_schema.Project, tags=["Projects"])
def read_project_endpoint(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None: raise HTTPException(status_code=404, detail="Project not found")
    return db_project
@app.put("/projects/{project_id}", response_model=project_schema.Project, tags=["Projects"])
def update_project_endpoint(project_id: int, project: project_schema.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = crud.update_project(db, project_id=project_id, project_update=project)
    if db_project is None: raise HTTPException(status_code=404, detail="Project not found")
    return db_project
@app.delete("/projects/{project_id}", response_model=project_schema.Project, tags=["Projects"])
def delete_project_endpoint(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.delete_project(db, project_id=project_id)
    if db_project is None: raise HTTPException(status_code=404, detail="Project not found")
    return db_project

# --- Endpoints per le FONTI ---
@app.post("/projects/{project_id}/sources/", response_model=source_schema.Source, tags=["Sources"])
def create_source_for_project_endpoint(project_id: int, source: source_schema.SourceCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None: raise HTTPException(status_code=404, detail="Project not found")
    return crud.create_project_source(db=db, source=source, project_id=project_id)
@app.get("/projects/{project_id}/sources/", response_model=List[source_schema.Source], tags=["Sources"])
def read_sources_for_project_endpoint(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None: raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_sources_for_project(db=db, project_id=project_id, skip=skip, limit=limit)
@app.put("/sources/{source_id}", response_model=source_schema.Source, tags=["Sources"])
def update_source_content_endpoint(source_id: int, source_update: source_schema.SourceUpdate, db: Session = Depends(get_db)):
    db_source = crud.update_source_content(db, source_id=source_id, content=source_update.content)
    if db_source is None: raise HTTPException(status_code=404, detail="Source not found")
    return db_source

# --- Run Server ---
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
