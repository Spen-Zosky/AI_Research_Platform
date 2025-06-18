# frontend_integration.py
"""
Codice da aggiungere al tuo app/main.py per integrare il frontend dashboard
"""

# AGGIUNGI QUESTI IMPORT AL TUO app/main.py ESISTENTE:

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import pandas as pd
from pathlib import Path

# AGGIUNGI QUESTE RIGHE DOPO LA CREAZIONE DELL'APP:

# Setup per frontend
static_dir = Path("app/static")
templates_dir = Path("app/templates")

# Crea le directory se non esistono
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Monta i file statici
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# AGGIUNGI QUESTE ROUTE FRONTEND AL TUO FILE:

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_redirect():
    """Redirect alla dashboard"""
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_main(request: Request, db: Session = Depends(get_db)):
    """Dashboard principale con statistiche"""
    try:
        # Recupera tutti i progetti con le loro fonti
        projects = crud.get_projects(db)
        
        # Calcola statistiche
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
    except Exception as e:
        # Fallback se i template non esistono ancora
        return HTMLResponse(f"""
        <html>
        <head><title>AI Research Platform</title></head>
        <body style="font-family: Arial; background: #0d1117; color: white; padding: 20px;">
            <h1>🚀 AI Research Platform</h1>
            <p>Dashboard frontend in configurazione...</p>
            <p>API disponibile su: <a href="/docs" style="color: #1f6feb;">/docs</a></p>
            <p>Errore: {str(e)}</p>
        </body>
        </html>
        """)

@app.get("/projects/view", response_class=HTMLResponse, tags=["Frontend"])
async def view_projects(request: Request, db: Session = Depends(get_db)):
    """Visualizza tutti i progetti"""
    try:
        projects = crud.get_projects(db)
        return templates.TemplateResponse("projects.html", {
            "request": request,
            "projects": projects
        })
    except Exception:
        return HTMLResponse("<h1>Template projects.html non trovato</h1>")

@app.get("/projects/{project_id}/view", response_class=HTMLResponse, tags=["Frontend"])
async def view_project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    """Dettaglio progetto"""
    try:
        project = crud.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Progetto non trovato")
        
        return templates.TemplateResponse("project_detail.html", {
            "request": request,
            "project": project
        })
    except Exception:
        return HTMLResponse(f"<h1>Progetto {project_id} non trovato</h1>")

@app.get("/search/view", response_class=HTMLResponse, tags=["Frontend"])
async def search_page(request: Request):
    """Pagina di ricerca"""
    try:
        return templates.TemplateResponse("search.html", {"request": request})
    except Exception:
        return HTMLResponse("""
        <html><body style="background: #0d1117; color: white; padding: 20px;">
        <h1>Ricerca</h1>
        <form action="/search/results" method="post">
            <input type="text" name="q" placeholder="Cerca..." required minlength="3" style="padding: 8px;">
            <button type="submit">Cerca</button>
        </form>
        </body></html>
        """)

@app.post("/search/results", response_class=HTMLResponse, tags=["Frontend"])
async def search_results(request: Request, q: str = Form(...), db: Session = Depends(get_db)):
    """Risultati ricerca"""
    try:
        results = crud.search_sources_content(db=db, query=q)
        return templates.TemplateResponse("search_results.html", {
            "request": request,
            "query": q,
            "results": results
        })
    except Exception as e:
        return HTMLResponse(f"""
        <html><body style="background: #0d1117; color: white; padding: 20px;">
        <h1>Risultati per: {q}</h1>
        <p>Errore nella ricerca: {str(e)}</p>
        <a href="/search/view">← Torna alla ricerca</a>
        </body></html>
        """)

@app.get("/import", response_class=HTMLResponse, tags=["Frontend"])
async def import_page(request: Request):
    """Pagina importazione"""
    try:
        return templates.TemplateResponse("import.html", {"request": request})
    except Exception:
        return HTMLResponse("""
        <html><body style="background: #0d1117; color: white; padding: 20px;">
        <h1>Importazione Dati</h1>
        <form action="/import/excel" method="post" enctype="multipart/form-data">
            <p>Nome Progetto: <input type="text" name="project_name" required></p>
            <p>File Excel: <input type="file" name="file" accept=".xlsx,.xls" required></p>
            <button type="submit">Importa</button>
        </form>
        </body></html>
        """)

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
            raise HTTPException(status_code=400, detail="File deve essere Excel")
        
        # Leggi il file
        contents = await file.read()
        df = pd.read_excel(contents)
        
        # Crea o recupera progetto
        # Nota: devi implementare get_project_by_name in crud.py
        project = None
        projects = crud.get_projects(db)
        for p in projects:
            if p.name.lower() == project_name.lower():
                project = p
                break
        
        if not project:
            project_data = project_schema.ProjectCreate(
                name=project_name,
                description=f"Progetto creato dall'importazione di {file.filename}"
            )
            project = crud.create_project(db, project_data)
        
        # Importa le fonti
        imported_count = 0
        for _, row in df.iterrows():
            title = str(row.get('Nome', row.get('Title', row.get('name', ''))))
            url = str(row.get('URL', row.get('Url', row.get('url', ''))))
            
            if title and url and title != 'nan' and url != 'nan':
                source_data = source_schema.SourceCreate(
                    title=title,
                    url=url,
                    project_id=project.id
                )
                try:
                    crud.create_source(db, source_data)
                    imported_count += 1
                except Exception as e:
                    print(f"Errore importazione fonte {title}: {e}")
        
        return RedirectResponse(
            url=f"/projects/{project.id}/view?imported={imported_count}",
            status_code=303
        )
        
    except Exception as e:
        return HTMLResponse(f"""
        <html><body style="background: #0d1117; color: white; padding: 20px;">
        <h1>Errore Importazione</h1>
        <p>{str(e)}</p>
        <a href="/import">← Torna all'importazione</a>
        </body></html>
        """)

# API HELPER PER FRONTEND

@app.get("/api/stats", tags=["Frontend API"])
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Statistiche per dashboard (JSON)"""
    try:
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
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/projects/quick", tags=["Frontend API"])
async def create_project_quick(
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    """Crea progetto veloce da form"""
    try:
        project_data = project_schema.ProjectCreate(name=name, description=description)
        project = crud.create_project(db, project_data)
        return {"success": True, "project_id": project.id, "message": f"Progetto '{name}' creato"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# FUNZIONE PER SETUP TEMPLATE
def setup_frontend_files():
    """Crea i file template se non esistono"""
    
    templates_dir = Path("app/templates")
    static_dir = Path("app/static")
    
    templates_dir.mkdir(exist_ok=True)
    static_dir.mkdir(exist_ok=True)
    
    # Template base dashboard.html (minimale)
    dashboard_html = '''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>AI Research Platform</title>
    <style>
        body { font-family: Arial; background: #0d1117; color: #e6edf3; padding: 20px; }
        .header { background: #161b22; padding: 16px; margin-bottom: 20px; border-radius: 6px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
        .stat-card { background: #161b22; padding: 16px; border-radius: 6px; border: 1px solid #30363d; }
        .stat-value { font-size: 24px; font-weight: bold; color: #f0f6fc; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #1f6feb; margin-right: 16px; text-decoration: none; }
        .projects { background: #161b22; padding: 16px; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AI Research Platform</h1>
        <div class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="/projects/view">Progetti</a>
            <a href="/search/view">Ricerca</a>
            <a href="/import">Importa</a>
            <a href="/docs">API</a>
        </div>
    </div>
    
    {% if stats %}
    <div class="stats">
        <div class="stat-card">
            <div>Progetti</div>
            <div class="stat-value">{{ stats.total_projects }}</div>
        </div>
        <div class="stat-card">
            <div>Fonti</div>
            <div class="stat-value">{{ stats.total_sources }}</div>
        </div>
        <div class="stat-card">
            <div>Elaborate</div>
            <div class="stat-value">{{ stats.sources_with_content }}</div>
        </div>
        <div class="stat-card">
            <div>Da elaborare</div>
            <div class="stat-value">{{ stats.sources_without_content }}</div>
        </div>
    </div>
    {% endif %}
    
    {% if projects %}
    <div class="projects">
        <h2>Progetti</h2>
        {% for project in projects %}
        <div style="margin: 10px 0; padding: 10px; background: #21262d; border-radius: 4px;">
            <strong>{{ project.name }}</strong> - {{ project.sources|length }} fonti
            <a href="/projects/{{ project.id }}/view" style="color: #1f6feb; margin-left: 10px;">Visualizza</a>
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>'''
    
    # Scrivi il template base
    dashboard_path = templates_dir / "dashboard.html"
    if not dashboard_path.exists():
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
    
    print(f"✅ Template creati in: {templates_dir}")
    print(f"✅ Directory static: {static_dir}")

# AGGIUNGI QUESTA CHIAMATA AL TUO APP STARTUP O MANUALMENTE:
# setup_frontend_files()
