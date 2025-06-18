# frontend_routes.py
"""
Route per il frontend dashboard da aggiungere al tuo app/main.py
"""

from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import pandas as pd
from pathlib import Path

from .core.database import get_db
from . import crud
from .schemas import project as project_schema, source as source_schema

# Aggiungi queste route al tuo app/main.py esistente

# Setup per servire file statici e template
static_dir = Path("app/static")
templates_dir = Path("app/templates")

# Crea le directory se non esistono
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Monta i file statici
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# === FRONTEND ROUTES ===

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_home(request: Request):
    """Dashboard principale"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_main(request: Request, db: Session = Depends(get_db)):
    """Dashboard con statistiche"""
    # Recupera statistiche
    projects = crud.get_projects(db)
    total_projects = len(projects)
    total_sources = sum(len(p.sources) for p in projects)
    sources_with_content = sum(1 for p in projects for s in p.sources if s.content)
    
    stats = {
        "total_projects": total_projects,
        "total_sources": total_sources,
        "sources_with_content": sources_with_content,
        "sources_without_content": total_sources - sources_with_content
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "projects": projects
    })

@app.get("/projects/view", response_class=HTMLResponse, tags=["Frontend"])
async def view_projects(request: Request, db: Session = Depends(get_db)):
    """Visualizza tutti i progetti"""
    projects = crud.get_projects(db)
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "projects": projects
    })

@app.get("/projects/{project_id}/view", response_class=HTMLResponse, tags=["Frontend"])
async def view_project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    """Dettaglio progetto con fonti"""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    
    return templates.TemplateResponse("project_detail.html", {
        "request": request,
        "project": project
    })

@app.get("/sources/view", response_class=HTMLResponse, tags=["Frontend"])
async def view_sources(request: Request, project_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Visualizza fonti (tutte o di un progetto)"""
    if project_id:
        project = crud.get_project(db, project_id)
        sources = project.sources if project else []
    else:
        # Recupera tutte le fonti da tutti i progetti
        projects = crud.get_projects(db)
        sources = [source for project in projects for source in project.sources]
    
    return templates.TemplateResponse("sources.html", {
        "request": request,
        "sources": sources,
        "project_id": project_id
    })

@app.get("/search/view", response_class=HTMLResponse, tags=["Frontend"])
async def search_page(request: Request):
    """Pagina di ricerca"""
    return templates.TemplateResponse("search.html", {"request": request})

@app.post("/search/results", response_class=HTMLResponse, tags=["Frontend"])
async def search_results(request: Request, q: str = Form(...), db: Session = Depends(get_db)):
    """Risultati ricerca"""
    results = crud.search_sources_content(db=db, query=q)
    return templates.TemplateResponse("search_results.html", {
        "request": request,
        "query": q,
        "results": results
    })

@app.get("/import", response_class=HTMLResponse, tags=["Frontend"])
async def import_page(request: Request):
    """Pagina importazione dati"""
    return templates.TemplateResponse("import.html", {"request": request})

@app.post("/import/excel", tags=["Frontend"])
async def import_excel_file(
    request: Request,
    file: UploadFile = File(...),
    project_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Importa dati da file Excel"""
    try:
        # Verifica tipo file
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File deve essere Excel (.xlsx/.xls)")
        
        # Leggi il file Excel
        contents = await file.read()
        df = pd.read_excel(contents)
        
        # Crea o recupera progetto
        project = crud.get_project_by_name(db, project_name)
        if not project:
            project_data = project_schema.ProjectCreate(
                name=project_name,
                description=f"Progetto creato dall'importazione di {file.filename}"
            )
            project = crud.create_project(db, project_data)
        
        # Importa le fonti
        imported_count = 0
        for _, row in df.iterrows():
            title = str(row.get('Nome', row.get('Title', '')))
            url = str(row.get('URL', row.get('Url', '')))
            
            if title and url:
                source_data = source_schema.SourceCreate(
                    title=title,
                    url=url,
                    project_id=project.id
                )
                crud.create_source(db, source_data)
                imported_count += 1
        
        return RedirectResponse(
            url=f"/projects/{project.id}/view?imported={imported_count}",
            status_code=303
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Errore importazione: {str(e)}")

# === API HELPERS PER FRONTEND ===

@app.get("/api/stats", tags=["Frontend API"])
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Statistiche per dashboard (JSON)"""
    projects = crud.get_projects(db)
    total_projects = len(projects)
    total_sources = sum(len(p.sources) for p in projects)
    sources_with_content = sum(1 for p in projects for s in p.sources if s.content)
    
    return {
        "total_projects": total_projects,
        "total_sources": total_sources,
        "sources_with_content": sources_with_content,
        "sources_without_content": total_sources - sources_with_content,
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "sources_count": len(p.sources),
                "sources_with_content": sum(1 for s in p.sources if s.content)
            }
            for p in projects
        ]
    }

@app.post("/api/projects/quick", tags=["Frontend API"])
async def create_project_quick(
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    """Crea progetto veloce da form"""
    project_data = project_schema.ProjectCreate(name=name, description=description)
    project = crud.create_project(db, project_data)
    return {"success": True, "project_id": project.id, "message": f"Progetto '{name}' creato"}

@app.delete("/api/projects/{project_id}", tags=["Frontend API"])
async def delete_project_api(project_id: int, db: Session = Depends(get_db)):
    """Elimina progetto"""
    success = crud.delete_project(db, project_id)
    if success:
        return {"success": True, "message": "Progetto eliminato"}
    else:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
