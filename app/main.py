import uvicorn
import time
from fastapi import FastAPI, Depends, HTTPException, Query, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import pandas as pd

from .core.database import get_db
from . import crud
from .schemas import project as project_schema, source as source_schema

# Create FastAPI app instance
app = FastAPI(
    title="AI Augmented Research Platform",
    description="Backend API for the research platform",
    version="2.0.0"
)

# Setup template e static files
static_dir = Path("app/static")
templates_dir = Path("app/templates")
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# === API ENDPOINTS ===

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

@app.get("/projects/", response_model=List[project_schema.Project], tags=["Projects"])
def read_projects_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_projects(db, skip=skip, limit=limit)

@app.get("/projects/{project_id}", response_model=project_schema.Project, tags=["Projects"])
def read_project_endpoint(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None: 
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.put("/projects/{project_id}", response_model=project_schema.Project, tags=["Projects"])
def update_project_endpoint(project_id: int, project: project_schema.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = crud.update_project(db, project_id=project_id, project_update=project)
    if db_project is None: 
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.delete("/projects/{project_id}", response_model=project_schema.Project, tags=["Projects"])
def delete_project_endpoint(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.delete_project(db, project_id=project_id)
    if db_project is None: 
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

# --- Endpoints per le FONTI ---
@app.post("/projects/{project_id}/sources/", response_model=source_schema.Source, tags=["Sources"])
def create_source_for_project_endpoint(project_id: int, source: source_schema.SourceCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None: 
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.create_project_source(db=db, source=source, project_id=project_id)

@app.get("/projects/{project_id}/sources/", response_model=List[source_schema.Source], tags=["Sources"])
def read_sources_for_project_endpoint(project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None: 
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_sources_for_project(db=db, project_id=project_id, skip=skip, limit=limit)

@app.put("/sources/{source_id}", response_model=source_schema.Source, tags=["Sources"])
def update_source_content_endpoint(source_id: int, source_update: source_schema.SourceUpdate, db: Session = Depends(get_db)):
    db_source = crud.update_source_content(db, source_id=source_id, content=source_update.content)
    if db_source is None: 
        raise HTTPException(status_code=404, detail="Source not found")
    return db_source

# --- API Stats Endpoint ---
@app.get("/api/stats", response_model=dict, tags=["API"])
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Restituisce le statistiche della dashboard in formato JSON.
    """
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
            "timestamp": int(time.time())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === FRONTEND ROUTES ===

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_redirect():
    """Redirect root to dashboard"""
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_main(request: Request, db: Session = Depends(get_db)):
    """
    Dashboard principale con statistiche e overview progetti.
    """
    try:
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

        return templates.TemplateResponse("dashboard_modern.html", {
            "request": request,
            "stats": stats,
            "projects": projects,
            "theme": "dark",
            "debug": False
        })
    except Exception as e:
        return HTMLResponse(f"""
        <html>
            <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                <h1>Dashboard Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/dashboard" style="color: #4a9eff;">← Retry</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/manage-projects", response_class=HTMLResponse, tags=["Frontend"])
async def view_projects(request: Request, db: Session = Depends(get_db)):
    """
    Pagina gestione progetti con lista completa.
    """
    try:
        projects = crud.get_projects(db)
        return templates.TemplateResponse("projects.html", {
            "request": request,
            "projects": projects,
            "theme": "dark"
        })
    except Exception as e:
        return HTMLResponse(f"""
        <html>
            <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                <h1>Projects Error</h1>
                <p>Error: {str(e)}</p>
                <a href="/dashboard" style="color: #4a9eff;">← Dashboard</a>
            </body>
        </html>
        """, status_code=500)

@app.get("/projects/{project_id}/view", response_class=HTMLResponse, tags=["Frontend"])
async def view_project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    """
    Visualizzazione dettaglio progetto con fonti.
    """
    try:
        project = crud.get_project(db, project_id=project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return templates.TemplateResponse("project_detail.html", {
            "request": request,
            "project": project,
            "theme": "dark"
        })
    except HTTPException:
        return HTMLResponse(f"""
        <html>
            <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                <h1>Project Not Found</h1>
                <p>Il progetto con ID {project_id} non è stato trovato.</p>
                <a href="/manage-projects" style="color: #4a9eff;">← Tutti i Progetti</a>
            </body>
        </html>
        """, status_code=404)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)

@app.get("/search/view", response_class=HTMLResponse, tags=["Frontend"])
async def search_page(request: Request, q: str = None, db: Session = Depends(get_db)):
    """
    Pagina ricerca avanzata con risultati.
    """
    try:
        projects = crud.get_projects(db)
        results = []
        search_time = 0
        
        if q and len(q) >= 3:
            # Perform search logic
            start_time = time.time()
            
            # Search in all sources
            for project in projects:
                for source in project.sources:
                    if source.content and q.lower() in source.content.lower():
                        # Create snippet with highlighted search term
                        content = source.content
                        query_pos = content.lower().find(q.lower())
                        
                        if query_pos != -1:
                            start = max(0, query_pos - 100)
                            end = min(len(content), query_pos + 200)
                            snippet = content[start:end]
                            
                            # Highlight search term (basic)
                            snippet = snippet.replace(
                                q, 
                                f'<mark style="background: #ffd700; color: #000;">{q}</mark>'
                            )
                            
                            if start > 0:
                                snippet = "..." + snippet
                            if end < len(content):
                                snippet = snippet + "..."
                        else:
                            snippet = content[:200] + "..." if len(content) > 200 else content
                        
                        results.append({
                            'title': source.name or source.url,
                            'project_id': project.id,
                            'project_name': project.name,
                            'source_id': source.id,
                            'url': source.url,
                            'snippet': snippet,
                            'created_at': source.created_at,
                            'tags': []  # Add tags if available in your schema
                        })
            
            search_time = round(time.time() - start_time, 3)
        
        return templates.TemplateResponse("search_modern.html", {
            "request": request,
            "query": q,
            "results": results,
            "search_time": search_time,
            "projects": projects,
            "total_pages": 1,
            "current_page": 1,
            "theme": "dark"
        })
    except Exception as e:
        return HTMLResponse(f"""
        <html>
            <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                <h1>Search Error</h1>
                <p>Error: {str(e)}</p>
                <form action="/search/view" method="get" style="margin: 20px 0;">
                    <input name="q" placeholder="Cerca..." style="padding: 10px; margin-right: 10px;">
                    <button type="submit" style="padding: 10px;">Search</button>
                </form>
                <a href="/dashboard" style="color: #4a9eff;">← Dashboard</a>
            </body>
        </html>
        """, status_code=500)

@app.post("/search/results", response_class=HTMLResponse, tags=["Frontend"])
async def search_results_post(request: Request, q: str = Form(...)):
    """
    Redirect POST search to GET with query parameter.
    """
    return RedirectResponse(url=f"/search/view?q={q}", status_code=302)

@app.get("/import", response_class=HTMLResponse, tags=["Frontend"])
async def import_page(request: Request):
    """
    Pagina importazione file Excel/CSV.
    """
    try:
        return templates.TemplateResponse("import.html", {
            "request": request,
            "theme": "dark"
        })
    except Exception as e:
        return HTMLResponse(f"""
        <html>
            <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                <h1>Import</h1>
                <form action="/import/excel" method="post" enctype="multipart/form-data" style="margin: 20px 0;">
                    <div style="margin: 10px 0;">
                        <label>Project Name:</label><br>
                        <input name="project_name" placeholder="Nome progetto" required style="padding: 10px; width: 300px;">
                    </div>
                    <div style="margin: 10px 0;">
                        <label>Excel File:</label><br>
                        <input type="file" name="file" accept=".xlsx,.xls,.csv" required style="padding: 10px;">
                    </div>
                    <button type="submit" style="padding: 10px 20px; background: #4a9eff; color: white; border: none;">Import</button>
                </form>
                <a href="/dashboard" style="color: #4a9eff;">← Dashboard</a>
            </body>
        </html>
        """)

@app.post("/import/excel", response_class=HTMLResponse, tags=["Frontend"])
async def import_excel_file(file: UploadFile = File(...), project_name: str = Form(...), db: Session = Depends(get_db)):
    """
    Importazione file Excel/CSV con creazione progetto e fonti.
    """
    try:
        # Validate file type
        allowed_extensions = ['.xlsx', '.xls', '.csv']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            return HTMLResponse(f"""
            <html>
                <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                    <h1>Error</h1>
                    <p>File must be Excel (.xlsx, .xls) or CSV format. Got: {file_extension}</p>
                    <a href="/import" style="color: #4a9eff;">← Back to Import</a>
                </body>
            </html>
            """, status_code=400)

        # Read file content
        contents = await file.read()
        
        # Parse file based on extension
        if file_extension == '.csv':
            df = pd.read_csv(contents)
        else:
            df = pd.read_excel(contents)

        # Validate required columns
        required_columns = ['Nome', 'URL']
        alt_columns = [['Name', 'Url'], ['Title', 'Link'], ['name', 'url']]
        
        column_mapping = {}
        for required in required_columns:
            if required in df.columns:
                column_mapping[required] = required
            else:
                # Try alternative column names
                found = False
                for alt_set in alt_columns:
                    for alt in alt_set:
                        if alt in df.columns:
                            column_mapping[required] = alt
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    return HTMLResponse(f"""
                    <html>
                        <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                            <h1>Error</h1>
                            <p>Required column '{required}' not found in file.</p>
                            <p>Available columns: {list(df.columns)}</p>
                            <p>Expected columns: Nome, URL (or Name, Url or Title, Link)</p>
                            <a href="/import" style="color: #4a9eff;">← Back to Import</a>
                        </body>
                    </html>
                    """, status_code=400)

        # Create or get project
        project = None
        projects = crud.get_projects(db)
        for p in projects:
            if p.name.lower() == project_name.lower():
                project = p
                break

        if not project:
            project_data = project_schema.ProjectCreate(
                name=project_name, 
                description=f"Imported from {file.filename} on {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            project = crud.create_project(db, project_data)

        # Import sources
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                title = str(row.get(column_mapping['Nome'], '')).strip()
                url = str(row.get(column_mapping['URL'], '')).strip()

                # Skip empty rows
                if not title or not url or title == 'nan' or url == 'nan':
                    skipped_count += 1
                    continue

                # Create source
                source_data = source_schema.SourceCreate(
                    name=title,
                    url=url,
                    project_id=project.id
                )
                
                crud.create_project_source(db, source_data, project.id)
                imported_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Error importing row {index}: {str(e)}")

        return HTMLResponse(f"""
        <html>
            <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                <h1>Import Completed Successfully! 🎉</h1>
                <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Import Summary</h3>
                    <p><strong>Project:</strong> {project.name}</p>
                    <p><strong>File:</strong> {file.filename}</p>
                    <p><strong>Sources Imported:</strong> {imported_count}</p>
                    <p><strong>Skipped (empty):</strong> {skipped_count}</p>
                    <p><strong>Errors:</strong> {error_count}</p>
                    <p><strong>Total Rows Processed:</strong> {len(df)}</p>
                </div>
                <div style="margin: 20px 0;">
                    <a href="/dashboard" style="background: #4a9eff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-right: 10px;">← Dashboard</a>
                    <a href="/projects/{project.id}/view" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-right: 10px;">View Project</a>
                    <a href="/import" style="background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Import Another</a>
                </div>
            </body>
        </html>
        """)

    except Exception as e:
        return HTMLResponse(f"""
        <html>
            <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                <h1>Import Error</h1>
                <div style="background: #d32f2f; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <strong>Error:</strong> {str(e)}
                </div>
                <p>Please check your file format and try again.</p>
                <div style="background: #2a2a2a; padding: 15px; border-radius: 4px; margin: 20px 0;">
                    <h4>File Requirements:</h4>
                    <ul>
                        <li>Excel (.xlsx, .xls) or CSV format</li>
                        <li>Must contain 'Nome' and 'URL' columns (or similar)</li>
                        <li>Rows with empty values will be skipped</li>
                    </ul>
                </div>
                <a href="/import" style="color: #4a9eff;">← Back to Import</a>
            </body>
        </html>
        """, status_code=500)

# --- Health Check ---
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": int(time.time()),
        "message": "AI Research Platform is running"
    }

# --- Run Server ---
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
