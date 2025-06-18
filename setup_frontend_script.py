# setup_frontend.py
"""
Script per configurare automaticamente il frontend della piattaforma
Esegui con: python setup_frontend.py
"""

import os
import sys
from pathlib import Path
import shutil

def create_directory_structure():
    """Crea la struttura di directory necessaria"""
    directories = [
        "app/templates",
        "app/static",
        "app/static/css",
        "app/static/js",
        "app/static/images"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory creata: {directory}")

def create_dashboard_template():
    """Crea il template dashboard principale"""
    template_content = '''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AI Research Platform{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: #0d1117;
            color: #e6edf3;
            line-height: 1.5;
        }
        .header {
            background-color: #161b22;
            border-bottom: 1px solid #30363d;
            padding: 16px 24px;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: #f0f6fc;
            font-size: 18px;
            font-weight: 600;
        }
        .logo::before {
            content: "🚀";
            margin-right: 8px;
            font-size: 24px;
        }
        .nav {
            display: flex;
            gap: 24px;
            align-items: center;
        }
        .nav-link {
            color: #e6edf3;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.15s ease;
            font-size: 14px;
        }
        .nav-link:hover {
            background-color: #21262d;
            color: #f0f6fc;
        }
        .nav-link.active {
            background-color: #1f6feb;
            color: #ffffff;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }
        .page-header {
            margin-bottom: 32px;
        }
        .page-title {
            font-size: 24px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 8px;
        }
        .page-subtitle {
            color: #7d8590;
            font-size: 16px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        .stat-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 16px;
            transition: border-color 0.15s ease;
        }
        .stat-card:hover {
            border-color: #7d8590;
        }
        .stat-label {
            font-size: 12px;
            color: #7d8590;
            font-weight: 500;
            margin-bottom: 4px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #f0f6fc;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid transparent;
            text-decoration: none;
            margin: 4px 8px 4px 0;
        }
        .btn-primary {
            background-color: #238636;
            color: #ffffff;
            border-color: #238636;
        }
        .btn-primary:hover {
            background-color: #2ea043;
            border-color: #2ea043;
        }
        .btn-secondary {
            background-color: #21262d;
            color: #f0f6fc;
            border-color: #30363d;
        }
        .btn-secondary:hover {
            background-color: #30363d;
            border-color: #7d8590;
        }
        .projects-list {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            overflow: hidden;
        }
        .project-item {
            padding: 16px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.15s ease;
        }
        .project-item:last-child {
            border-bottom: none;
        }
        .project-item:hover {
            background-color: #21262d;
        }
        .project-info h3 {
            color: #f0f6fc;
            font-size: 16px;
            margin-bottom: 4px;
        }
        .project-meta {
            color: #7d8590;
            font-size: 14px;
        }
        .actions-section {
            margin-bottom: 32px;
        }
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }
        .action-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            transition: all 0.15s ease;
        }
        .action-card:hover {
            border-color: #7d8590;
            transform: translateY(-1px);
        }
        .action-header {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }
        .action-icon {
            margin-right: 12px;
            font-size: 20px;
        }
        .action-title {
            font-size: 16px;
            font-weight: 600;
            color: #f0f6fc;
        }
        .action-description {
            color: #7d8590;
            margin-bottom: 16px;
            line-height: 1.4;
        }
        .form-group {
            margin-bottom: 16px;
        }
        .form-label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #f0f6fc;
            margin-bottom: 6px;
        }
        .form-input {
            width: 100%;
            padding: 8px 12px;
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #e6edf3;
            font-size: 14px;
            transition: border-color 0.15s ease;
        }
        .form-input:focus {
            outline: none;
            border-color: #1f6feb;
            box-shadow: 0 0 0 3px rgba(31, 111, 235, 0.3);
        }
        .alert {
            padding: 12px 16px;
            border-radius: 6px;
            margin: 16px 0;
            font-size: 14px;
            border-left: 4px solid;
        }
        .alert.success {
            background-color: #0f2419;
            color: #3fb950;
            border-color: #3fb950;
        }
        .alert.info {
            background-color: #0f1419;
            color: #1f6feb;
            border-color: #1f6feb;
        }
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 16px;
            }
            .nav {
                flex-wrap: wrap;
                justify-content: center;
            }
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .actions-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <a href="/dashboard" class="logo">AI Research Platform</a>
            <nav class="nav">
                <a href="/dashboard" class="nav-link">Dashboard</a>
                <a href="/projects/view" class="nav-link">Progetti</a>
                <a href="/search/view" class="nav-link">Ricerca</a>
                <a href="/import" class="nav-link">Importa</a>
                <a href="/docs" class="nav-link" target="_blank">API</a>
            </nav>
        </div>
    </header>

    <main class="container">
        {% block content %}
        <div class="page-header">
            <h1 class="page-title">Dashboard</h1>
            <p class="page-subtitle">Panoramica generale della piattaforma di ricerca</p>
        </div>

        {% if stats %}
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Progetti Totali</div>
                <div class="stat-value">{{ stats.total_projects }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Fonti Totali</div>
                <div class="stat-value">{{ stats.total_sources }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Con Contenuto</div>
                <div class="stat-value">{{ stats.sources_with_content }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Da Elaborare</div>
                <div class="stat-value">{{ stats.sources_without_content }}</div>
            </div>
        </div>
        {% endif %}

        <div class="actions-section">
            <h2 class="section-title">🚀 Azioni Rapide</h2>
            <div class="actions-grid">
                <div class="action-card">
                    <div class="action-header">
                        <span class="action-icon">📁</span>
                        <span class="action-title">Nuovo Progetto</span>
                    </div>
                    <div class="action-description">
                        Crea un nuovo progetto di ricerca per organizzare le tue fonti
                    </div>
                    <a href="/projects/view" class="btn btn-primary">Gestisci Progetti</a>
                </div>

                <div class="action-card">
                    <div class="action-header">
                        <span class="action-icon">📥</span>
                        <span class="action-title">Importa Dati</span>
                    </div>
                    <div class="action-description">
                        Importa fonti da file Excel, CSV o altri formati supportati
                    </div>
                    <a href="/import" class="btn btn-primary">Importa File</a>
                </div>

                <div class="action-card">
                    <div class="action-header">
                        <span class="action-icon">🔍</span>
                        <span class="action-title">Ricerca Contenuti</span>
                    </div>
                    <div class="action-description">
                        Cerca nel contenuto di tutte le fonti elaborate
                    </div>
                    <a href="/search/view" class="btn btn-primary">Cerca</a>
                </div>

                <div class="action-card">
                    <div class="action-header">
                        <span class="action-icon">📊</span>
                        <span class="action-title">API Endpoint</span>
                    </div>
                    <div class="action-description">
                        Accedi alla documentazione API per integrazioni avanzate
                    </div>
                    <a href="/docs" class="btn btn-primary" target="_blank">Apri API Docs</a>
                </div>
            </div>
        </div>

        {% if projects %}
        <div class="actions-section">
            <h2 class="section-title">📁 Progetti Recenti</h2>
            <div class="projects-list">
                {% for project in projects[:5] %}
                <div class="project-item">
                    <div class="project-info">
                        <h3>{{ project.name }}</h3>
                        <div class="project-meta">
                            {{ project.description or 'Nessuna descrizione' }}
                        </div>
                    </div>
                    <div>
                        <span>{{ project.sources|length }} fonti</span>
                        <a href="/projects/{{ project.id }}/view" class="btn btn-secondary">Visualizza</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        {% endblock %}
    </main>

    <script>
        // Aggiorna statistiche ogni 30 secondi
        setInterval(async function() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                const statValues = document.querySelectorAll('.stat-value');
                if (statValues.length >= 4) {
                    statValues[0].textContent = stats.total_projects;
                    statValues[1].textContent = stats.total_sources;
                    statValues[2].textContent = stats.sources_with_content;
                    statValues[3].textContent = stats.sources_without_content;
                }
            } catch (error) {
                console.log('Errore aggiornamento statistiche:', error);
            }
        }, 30000);
    </script>
</body>
</html>'''
    
    template_path = Path("app/templates/dashboard.html")
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ Template dashboard creato: {template_path}")

def create_simple_templates():
    """Crea template semplici per le altre pagine"""
    
    templates = {
        "search.html": '''{% extends "dashboard.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title">Ricerca Contenuti</h1>
    <p class="page-subtitle">Cerca nel contenuto di tutte le fonti elaborate</p>
</div>

<div class="action-card" style="max-width: 600px; margin: 0 auto;">
    <form action="/search/results" method="post">
        <div class="form-group">
            <label class="form-label">Termini di ricerca</label>
            <input type="text" name="q" class="form-input" required minlength="3" 
                   placeholder="Inserisci almeno 3 caratteri...">
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%;">🔍 Cerca</button>
    </form>
</div>
{% endblock %}''',

        "import.html": '''{% extends "dashboard.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title">Importazione Dati</h1>
    <p class="page-subtitle">Importa fonti da file Excel o CSV</p>
</div>

<div class="action-card" style="max-width: 600px; margin: 0 auto;">
    <form action="/import/excel" method="post" enctype="multipart/form-data">
        <div class="form-group">
            <label class="form-label">Nome Progetto</label>
            <input type="text" name="project_name" class="form-input" required 
                   placeholder="Es: Ricerca Mercato 2024">
        </div>
        <div class="form-group">
            <label class="form-label">File Excel</label>
            <input type="file" name="file" class="form-input" required accept=".xlsx,.xls">
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%;">📥 Importa File</button>
    </form>
</div>

<div class="alert info" style="max-width: 600px; margin: 32px auto 0;">
    <strong>Formato supportato:</strong><br>
    Il file Excel deve contenere almeno le colonne 'Nome' e 'URL'.
</div>
{% endblock %}''',

        "projects.html": '''{% extends "dashboard.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title">Gestione Progetti</h1>
    <p class="page-subtitle">Tutti i progetti di ricerca</p>
</div>

{% if projects %}
<div class="projects-list">
    {% for project in projects %}
    <div class="project-item">
        <div class="project-info">
            <h3>{{ project.name }}</h3>
            <div class="project-meta">
                {{ project.description or 'Nessuna descrizione' }} • 
                {{ project.sources|length }} fonti • 
                Creato il {{ project.created_at.strftime('%d/%m/%Y') }}
            </div>
        </div>
        <div>
            <a href="/projects/{{ project.id }}/view" class="btn btn-primary">Visualizza</a>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="alert info">
    <strong>Nessun progetto trovato</strong><br>
    Inizia creando il tuo primo progetto dalla dashboard.
</div>
{% endif %}
{% endblock %}'''
    }
    
    for filename, content in templates.items():
        template_path = Path(f"app/templates/{filename}")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Template creato: {template_path}")

def update_main_py():
    """Aggiorna il file main.py con le route frontend"""
    main_py_path = Path("app/main.py")
    
    if not main_py_path.exists():
        print("❌ File app/main.py non trovato!")
        return False
    
    # Leggi il contenuto attuale
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Aggiungi imports se non presenti
    imports_to_add = [
        "from fastapi.responses import HTMLResponse, RedirectResponse",
        "from fastapi.staticfiles import StaticFiles",
        "from fastapi.templating import Jinja2Templates",
        "from fastapi import Request, Form, UploadFile, File",
        "import pandas as pd",
        "from pathlib import Path"
    ]
    
    # Frontend setup code
    frontend_setup = '''
# === FRONTEND SETUP ===
static_dir = Path("app/static")
templates_dir = Path("app/templates")
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# === FRONTEND ROUTES ===
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_redirect():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard_main(request: Request, db: Session = Depends(get_db)):
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
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats,
            "projects": projects
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Dashboard Error: {str(e)}</h1>")

@app.get("/projects/view", response_class=HTMLResponse, tags=["Frontend"])
async def view_projects(request: Request, db: Session = Depends(get_db)):
    try:
        projects = crud.get_projects(db)
        return templates.TemplateResponse("projects.html", {
            "request": request,
            "projects": projects
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Projects Error: {str(e)}</h1>")

@app.get("/search/view", response_class=HTMLResponse, tags=["Frontend"])
async def search_page(request: Request):
    try:
        return templates.TemplateResponse("search.html", {"request": request})
    except Exception:
        return HTMLResponse("<h1>Search form</h1><form action='/search/results' method='post'><input name='q' required><button type='submit'>Search</button></form>")

@app.post("/search/results", response_class=HTMLResponse, tags=["Frontend"])
async def search_results(request: Request, q: str = Form(...), db: Session = Depends(get_db)):
    try:
        results = crud.search_sources_content(db=db, query=q)
        return HTMLResponse(f"<h1>Results for: {q}</h1><p>Found {len(results)} results</p><a href='/search/view'>← Back</a>")
    except Exception as e:
        return HTMLResponse(f"<h1>Search Error: {str(e)}</h1>")

@app.get("/import", response_class=HTMLResponse, tags=["Frontend"])
async def import_page(request: Request):
    try:
        return templates.TemplateResponse("import.html", {"request": request})
    except Exception:
        return HTMLResponse("<h1>Import</h1><form action='/import/excel' method='post' enctype='multipart/form-data'><input name='project_name' placeholder='Project name' required><input type='file' name='file' accept='.xlsx,.xls' required><button type='submit'>Import</button></form>")

@app.post("/import/excel", tags=["Frontend"])
async def import_excel_file(file: UploadFile = File(...), project_name: str = Form(...), db: Session = Depends(get_db)):
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            return HTMLResponse("<h1>Error: File must be Excel format</h1>")
        
        contents = await file.read()
        df = pd.read_excel(contents)
        
        # Create or get project
        project = None
        projects = crud.get_projects(db)
        for p in projects:
            if p.name.lower() == project_name.lower():
                project = p
                break
        
        if not project:
            from .schemas import project as project_schema
            project_data = project_schema.ProjectCreate(name=project_name, description=f"Imported from {file.filename}")
            project = crud.create_project(db, project_data)
        
        # Import sources
        imported_count = 0
        for _, row in df.iterrows():
            title = str(row.get('Nome', row.get('Title', row.get('name', ''))))
            url = str(row.get('URL', row.get('Url', row.get('url', ''))))
            
            if title and url and title != 'nan' and url != 'nan':
                from .schemas import source as source_schema
                source_data = source_schema.SourceCreate(title=title, url=url, project_id=project.id)
                try:
                    crud.create_source(db, source_data)
                    imported_count += 1
                except:
                    pass
        
        return HTMLResponse(f"<h1>Import Success</h1><p>Imported {imported_count} sources to project '{project_name}'</p><a href='/dashboard'>← Dashboard</a>")
        
    except Exception as e:
        return HTMLResponse(f"<h1>Import Error: {str(e)}</h1>")

@app.get("/api/stats", tags=["Frontend API"])
async def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        projects = crud.get_projects(db)
        total_projects = len(projects)
        total_sources = sum(len(p.sources) for p in projects)
        sources_with_content = sum(1 for p in projects for s in p.sources if s.content)
        
        return {
            "total_projects": total_projects,
            "total_sources": total_sources,
            "sources_with_content": sources_with_content,
            "sources_without_content": total_sources - sources_with_content
        }
    except Exception as e:
        return {"error": str(e)}
'''
    
    # Crea backup
    backup_path = main_py_path.with_suffix('.py.backup')
    shutil.copy2(main_py_path, backup_path)
    print(f"✅ Backup creato: {backup_path}")
    
    # Aggiungi il codice frontend
    updated_content = content + frontend_setup
    
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ File {main_py_path} aggiornato con route frontend")
    return True

def install_dependencies():
    """Installa le dipendenze necessarie"""
    dependencies = [
        "jinja2",
        "python-multipart",
        "aiofiles",
        "pandas",
        "openpyxl"
    ]
    
    print("📦 Installazione dipendenze...")
    for dep in dependencies:
        os.system(f"pip install {dep}")
        print(f"✅ Installato: {dep}")

def main():
    """Funzione principale di setup"""
    print("🚀 SETUP FRONTEND AI RESEARCH PLATFORM")
    print("=" * 50)
    
    try:
        print("\n1. Creazione struttura directory...")
        create_directory_structure()
        
        print("\n2. Installazione dipendenze...")
        install_dependencies()
        
        print("\n3. Creazione template...")
        create_dashboard_template()
        create_simple_templates()
        
        print("\n4. Aggiornamento main.py...")
        if update_main_py():
            print("✅ FastAPI aggiornato con successo")
        else:
            print("❌ Errore nell'aggiornamento di main.py")
        
        print("\n" + "=" * 50)
        print("🎉 SETUP COMPLETATO!")
        print("=" * 50)
        print()
        print("📋 PROSSIMI PASSI:")
        print("1. Riavvia il server FastAPI:")
        print("   python -m app.main")
        print()
        print("2. Apri il browser su:")
        print("   http://127.0.0.1:8000/dashboard")
        print()
        print("3. Il tuo frontend è ora integrato!")
        print("   • Dashboard: http://127.0.0.1:8000/dashboard")
        print("   • Progetti: http://127.0.0.1:8000/projects/view")
        print("   • Ricerca:  http://127.0.0.1:8000/search/view")
        print("   • Import:   http://127.0.0.1:8000/import")
        print("   • API Docs: http://127.0.0.1:8000/docs")
        print()
        print("🔧 FILE CREATI:")
        print(f"   • app/templates/dashboard.html")
        print(f"   • app/templates/search.html")
        print(f"   • app/templates/import.html")
        print(f"   • app/templates/projects.html")
        print(f"   • app/static/ (directory)")
        print(f"   • app/main.py.backup (backup originale)")
        print()
        print("✨ Il tuo sistema è ora completo con frontend integrato!")
        
    except Exception as e:
        print(f"❌ ERRORE DURANTE IL SETUP: {e}")
        print("\nIn caso di problemi:")
        print("1. Verifica di essere nella directory corretta del progetto")
        print("2. Assicurati che il virtual environment sia attivo")
        print("3. Controlla che app/main.py esista")
        return False
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Frontend AI Research Platform")
    parser.add_argument("--force", action="store_true", help="Sovrascrivi file esistenti")
    parser.add_argument("--minimal", action="store_true", help="Setup minimale senza dipendenze")
    
    args = parser.parse_args()
    
    if args.minimal:
        print("🔧 Setup minimale...")
        create_directory_structure()
        create_dashboard_template()
        create_simple_templates()
        print("✅ Setup minimale completato")
    else:
        success = main()
        exit(0 if success else 1)