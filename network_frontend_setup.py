# setup_frontend_network.py
"""
Setup completo frontend + configurazione di rete per VM Proxmox
"""

import os
import sys
import socket
import subprocess
from pathlib import Path
import shutil

def get_vm_ip():
    """Rileva IP della VM automaticamente"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        vm_ip = s.getsockname()[0]
        s.close()
        return vm_ip
    except:
        return input("Inserisci IP della VM (es. 192.168.1.100): ").strip()

def create_network_ready_templates(vm_ip):
    """Crea template HTML configurati per accesso di rete"""
    
    # Template dashboard con URL di rete
    dashboard_template = f'''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Research Platform</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: #0d1117;
            color: #e6edf3;
            line-height: 1.5;
        }}
        .header {{
            background-color: #161b22;
            border-bottom: 1px solid #30363d;
            padding: 16px 24px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{
            display: flex;
            align-items: center;
            text-decoration: none;
            color: #f0f6fc;
            font-size: 18px;
            font-weight: 600;
        }}
        .logo::before {{
            content: "🚀";
            margin-right: 8px;
            font-size: 24px;
        }}
        .nav {{
            display: flex;
            gap: 24px;
            align-items: center;
        }}
        .nav-link {{
            color: #e6edf3;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.15s ease;
            font-size: 14px;
        }}
        .nav-link:hover {{
            background-color: #21262d;
            color: #f0f6fc;
        }}
        .nav-link.active {{
            background-color: #1f6feb;
            color: #ffffff;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }}
        .page-header {{
            margin-bottom: 32px;
        }}
        .page-title {{
            font-size: 24px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 8px;
        }}
        .page-subtitle {{
            color: #7d8590;
            font-size: 16px;
        }}
        .network-info {{
            background: linear-gradient(135deg, #1f6feb, #7c3aed);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
            color: white;
            text-align: center;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .stat-card {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 16px;
            transition: border-color 0.15s ease;
        }}
        .stat-card:hover {{
            border-color: #7d8590;
        }}
        .stat-label {{
            font-size: 12px;
            color: #7d8590;
            font-weight: 500;
            margin-bottom: 4px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 700;
            color: #f0f6fc;
        }}
        .actions-section {{
            margin-bottom: 32px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .actions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}
        .action-card {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            transition: all 0.15s ease;
        }}
        .action-card:hover {{
            border-color: #7d8590;
            transform: translateY(-1px);
        }}
        .action-header {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }}
        .action-icon {{
            margin-right: 12px;
            font-size: 20px;
        }}
        .action-title {{
            font-size: 16px;
            font-weight: 600;
            color: #f0f6fc;
        }}
        .action-description {{
            color: #7d8590;
            margin-bottom: 16px;
            line-height: 1.4;
        }}
        .btn {{
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
        }}
        .btn-primary {{
            background-color: #238636;
            color: #ffffff;
            border-color: #238636;
        }}
        .btn-primary:hover {{
            background-color: #2ea043;
            border-color: #2ea043;
        }}
        .btn-secondary {{
            background-color: #21262d;
            color: #f0f6fc;
            border-color: #30363d;
        }}
        .btn-secondary:hover {{
            background-color: #30363d;
            border-color: #7d8590;
        }}
        .projects-list {{
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            overflow: hidden;
        }}
        .project-item {{
            padding: 16px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.15s ease;
        }}
        .project-item:last-child {{
            border-bottom: none;
        }}
        .project-item:hover {{
            background-color: #21262d;
        }}
        .project-info h3 {{
            color: #f0f6fc;
            font-size: 16px;
            margin-bottom: 4px;
        }}
        .project-meta {{
            color: #7d8590;
            font-size: 14px;
        }}
        @media (max-width: 768px) {{
            .header-content {{
                flex-direction: column;
                gap: 16px;
            }}
            .nav {{
                flex-wrap: wrap;
                justify-content: center;
            }}
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .actions-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <a href="/dashboard" class="logo">AI Research Platform</a>
            <nav class="nav">
                <a href="/dashboard" class="nav-link active">Dashboard</a>
                <a href="/projects/view" class="nav-link">Progetti</a>
                <a href="/search/view" class="nav-link">Ricerca</a>
                <a href="/import" class="nav-link">Importa</a>
                <a href="/docs" class="nav-link" target="_blank">API</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <div class="network-info">
            <strong>🌐 Accesso di Rete Attivo</strong><br>
            Server VM: {vm_ip}:8000 • Accessibile da tutta la rete locale
        </div>

        <div class="page-header">
            <h1 class="page-title">Dashboard</h1>
            <p class="page-subtitle">Piattaforma AI di ricerca - Accesso rete locale</p>
        </div>

        {{%% if stats %%}}
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Progetti Totali</div>
                <div class="stat-value">{{{{ stats.total_projects }}}}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Fonti Totali</div>
                <div class="stat-value">{{{{ stats.total_sources }}}}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Con Contenuto</div>
                <div class="stat-value">{{{{ stats.sources_with_content }}}}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Da Elaborare</div>
                <div class="stat-value">{{{{ stats.sources_without_content }}}}</div>
            </div>
        </div>
        {{%% endif %%}}

        <div class="actions-section">
            <h2 class="section-title">🚀 Azioni Rapide</h2>
            <div class="actions-grid">
                <div class="action-card">
                    <div class="action-header">
                        <span class="action-icon">📁</span>
                        <span class="action-title">Gestisci Progetti</span>
                    </div>
                    <div class="action-description">
                        Visualizza e gestisci tutti i progetti di ricerca
                    </div>
                    <a href="/projects/view" class="btn btn-primary">Visualizza Progetti</a>
                </div>

                <div class="action-card">
                    <div class="action-header">
                        <span class="action-icon">📥</span>
                        <span class="action-title">Importa Dati</span>
                    </div>
                    <div class="action-description">
                        Carica fonti da file Excel, CSV o altri formati
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
                    <a href="/search/view" class="btn btn-primary">Avvia Ricerca</a>
                </div>

                <div class="action-card">
                    <div class="action-header">
                        <span class="action-icon">📊</span>
                        <span class="action-title">API Documentation</span>
                    </div>
                    <div class="action-description">
                        Documentazione tecnica API per integrazioni
                    </div>
                    <a href="/docs" class="btn btn-primary" target="_blank">Apri Docs</a>
                </div>
            </div>
        </div>

        {{%% if projects %%}}
        <div class="actions-section">
            <h2 class="section-title">📁 Progetti Recenti</h2>
            <div class="projects-list">
                {{%% for project in projects[:5] %%}}
                <div class="project-item">
                    <div class="project-info">
                        <h3>{{{{ project.name }}}}</h3>
                        <div class="project-meta">
                            {{{{ project.description or 'Nessuna descrizione' }}}} • {{{{ project.sources|length }}}} fonti
                        </div>
                    </div>
                    <div>
                        <a href="/projects/{{{{ project.id }}}}/view" class="btn btn-secondary">Visualizza</a>
                    </div>
                </div>
                {{%% endfor %%}}
            </div>
        </div>
        {{%% endif %%}}
    </main>

    <script>
        // Configurazione per accesso di rete
        const API_BASE_URL = "http://{vm_ip}:8000";
        
        // Aggiorna statistiche ogni 30 secondi
        setInterval(async function() {{
            try {{
                const response = await fetch(API_BASE_URL + '/api/stats');
                const stats = await response.json();
                
                const statValues = document.querySelectorAll('.stat-value');
                if (statValues.length >= 4) {{
                    statValues[0].textContent = stats.total_projects;
                    statValues[1].textContent = stats.total_sources;
                    statValues[2].textContent = stats.sources_with_content;
                    statValues[3].textContent = stats.sources_without_content;
                }}
            }} catch (error) {{
                console.log('Errore aggiornamento statistiche:', error);
            }}
        }}, 30000);

        // Test connettività di rete
        async function testNetworkConnectivity() {{
            try {{
                const response = await fetch(API_BASE_URL + '/api/stats');
                if (response.ok) {{
                    console.log('✅ Connessione di rete OK');
                    return true;
                }}
            }} catch (error) {{
                console.error('❌ Errore connessione di rete:', error);
                return false;
            }}
        }}

        // Test iniziale
        document.addEventListener('DOMContentLoaded', function() {{
            testNetworkConnectivity();
        }});
    </script>
</body>
</html>'''
    
    # Salva template
    templates_dir = Path("app/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    with open(templates_dir / "dashboard.html", 'w', encoding='utf-8') as f:
        f.write(dashboard_template)
    
    print(f"✅ Template dashboard creato per IP {vm_ip}")

def update_fastapi_for_network(vm_ip):
    """Aggiorna FastAPI per accesso di rete"""
    
    network_config = f'''
# === CONFIGURAZIONE ACCESSO DI RETE ===
from fastapi.middleware.cors import CORSMiddleware

# Configura CORS per accesso da rete locale
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://{vm_ip}:8000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # Per sviluppo - in produzione limitare agli IP della rete
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === FRONTEND SETUP PER RETE ===
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form, UploadFile, File
import pandas as pd
from pathlib import Path

static_dir = Path("app/static")
templates_dir = Path("app/templates")
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Route principali
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
        
        stats = {{
            "total_projects": total_projects,
            "total_sources": total_sources,
            "sources_with_content": sources_with_content,
            "sources_without_content": total_sources - sources_with_content
        }}
        
        return templates.TemplateResponse("dashboard.html", {{
            "request": request,
            "stats": stats,
            "projects": projects
        }})
    except Exception as e:
        return HTMLResponse(f"""
        <html>
        <head><title>AI Research Platform</title></head>
        <body style="font-family: Arial; background: #0d1117; color: white; padding: 20px;">
            <h1>🚀 AI Research Platform</h1>
            <h2>🌐 Accesso di Rete: {vm_ip}:8000</h2>
            <p>Dashboard in configurazione...</p>
            <p><a href="/docs" style="color: #1f6feb;">📚 API Documentation</a></p>
            <div style="background: #161b22; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <strong>Errore:</strong> {{str(e)}}
            </div>
        </body>
        </html>
        """)

@app.get("/projects/view", response_class=HTMLResponse, tags=["Frontend"])
async def view_projects(request: Request, db: Session = Depends(get_db)):
    try:
        projects = crud.get_projects(db)
        return HTMLResponse(f"""
        <html>
        <body style="font-family: Arial; background: #0d1117; color: white; padding: 20px;">
            <h1>📁 Progetti</h1>
            <p>Progetti totali: {{len(projects)}}</p>
            {{%% for project in projects %%}}
            <div style="background: #161b22; padding: 15px; margin: 10px 0; border-radius: 8px;">
                <h3>{{project.name}}</h3>
                <p>Fonti: {{len(project.sources)}}</p>
            </div>
            {{%% endfor %%}}
            <a href="/dashboard">← Dashboard</a>
        </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(f"<h1>Errore progetti: {{str(e)}}</h1>")

@app.get("/search/view", response_class=HTMLResponse, tags=["Frontend"])
async def search_page(request: Request):
    return HTMLResponse(f"""
    <html>
    <body style="font-family: Arial; background: #0d1117; color: white; padding: 20px;">
        <h1>🔍 Ricerca</h1>
        <form action="/search/results" method="post" style="margin: 20px 0;">
            <input type="text" name="q" placeholder="Cerca..." required minlength="3" 
                   style="padding: 10px; font-size: 16px; width: 300px; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: white;">
            <button type="submit" style="padding: 10px 20px; background: #238636; color: white; border: none; border-radius: 6px; margin-left: 10px;">Cerca</button>
        </form>
        <a href="/dashboard">← Dashboard</a>
    </body>
    </html>
    """)

@app.post("/search/results", response_class=HTMLResponse, tags=["Frontend"])
async def search_results(request: Request, q: str = Form(...), db: Session = Depends(get_db)):
    try:
        results = crud.search_sources_content(db=db, query=q)
        return HTMLResponse(f"""
        <html>
        <body style="font-family: Arial; background: #0d1117; color: white; padding: 20px;">
            <h1>🔍 Risultati per: "{{q}}"</h1>
            <p>Trovati {{len(results)}} risultati</p>
            {{%% for result in results %%}}
            <div style="background: #161b22; padding: 15px; margin: 10px 0; border-radius: 8px;">
                <h3>{{result.title}}</h3>
                <p><a href="{{result.url}}" target="_blank" style="color: #1f6feb;">{{result.url}}</a></p>
            </div>
            {{%% endfor %%}}
            <a href="/search/view">← Nuova ricerca</a>
        </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(f"<h1>Errore ricerca: {{str(e)}}</h1>")

@app.get("/import", response_class=HTMLResponse, tags=["Frontend"])
async def import_page(request: Request):
    return HTMLResponse(f"""
    <html>
    <body style="font-family: Arial; background: #0d1117; color: white; padding: 20px;">
        <h1>📥 Importazione Dati</h1>
        <form action="/import/excel" method="post" enctype="multipart/form-data" style="margin: 20px 0;">
            <div style="margin: 15px 0;">
                <label>Nome Progetto:</label><br>
                <input type="text" name="project_name" required placeholder="Es: Ricerca 2024" 
                       style="padding: 10px; width: 300px; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: white;">
            </div>
            <div style="margin: 15px 0;">
                <label>File Excel:</label><br>
                <input type="file" name="file" accept=".xlsx,.xls" required 
                       style="padding: 10px; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: white;">
            </div>
            <button type="submit" style="padding: 10px 20px; background: #238636; color: white; border: none; border-radius: 6px;">📥 Importa</button>
        </form>
        <a href="/dashboard">← Dashboard</a>
    </body>
    </html>
    """)

@app.post("/import/excel", tags=["Frontend"])
async def import_excel_file(file: UploadFile = File(...), project_name: str = Form(...), db: Session = Depends(get_db)):
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            return HTMLResponse("<h1>Errore: File deve essere Excel</h1>")
        
        contents = await file.read()
        df = pd.read_excel(contents)
        
        # Trova o crea progetto
        project = None
        projects = crud.get_projects(db)
        for p in projects:
            if p.name.lower() == project_name.lower():
                project = p
                break
        
        if not project:
            from .schemas import project as project_schema
            project_data = project_schema.ProjectCreate(name=project_name, description=f"Importato da {{file.filename}}")
            project = crud.create_project(db, project_data)
        
        # Importa fonti
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
        
        return HTMLResponse(f"""
        <html>
        <body style="font-family: Arial; background: #0d1117; color: white; padding: 20px;">
            <h1>✅ Importazione Completata</h1>
            <p>Importate {{imported_count}} fonti nel progetto "{{project_name}}"</p>
            <p><a href="/projects/{{project.id}}/view" style="color: #1f6feb;">Visualizza progetto</a></p>
            <p><a href="/dashboard">← Dashboard</a></p>
        </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(f"<h1>Errore importazione: {{str(e)}}</h1>")

@app.get("/api/stats", tags=["Frontend API"])
async def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        projects = crud.get_projects(db)
        total_projects = len(projects)
        total_sources = sum(len(p.sources) for p in projects)
        sources_with_content = sum(1 for p in projects for s in p.sources if s.content)
        
        return {{
            "total_projects": total_projects,
            "total_sources": total_sources,
            "sources_with_content": sources_with_content,
            "sources_without_content": total_sources - sources_with_content,
            "vm_ip": "{vm_ip}",
            "network_ready": True
        }}
    except Exception as e:
        return {{"error": str(e)}}

# Info di rete
@app.get("/network-info", response_class=HTMLResponse, tags=["Network"])
async def network_info():
    return HTMLResponse(f"""
    <html>
    <head><title>Network Info - AI Research Platform</title></head>
    <body style="font-family: Arial; background: #0d1117; color: white; padding: 20px;">
        <h1>🌐 Informazioni Accesso di Rete</h1>
        <div style="background: #161b22; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2>📍 Configurazione Attuale</h2>
            <p><strong>IP VM:</strong> {vm_ip}</p>
            <p><strong>Porta:</strong> 8000</p>
            <p><strong>Stato:</strong> ✅ Accesso di rete attivo</p>
        </div>
        
        <div style="background: #161b22; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2>🔗 URL di Accesso</h2>
            <p><strong>Dashboard:</strong> <a href="http://{vm_ip}:8000/dashboard" style="color: #1f6feb;">http://{vm_ip}:8000/dashboard</a></p>
            <p><strong>API Docs:</strong> <a href="http://{vm_ip}:8000/docs" style="color: #1f6feb;">http://{vm_ip}:8000/docs</a></p>
            <p><strong>Ricerca:</strong> <a href="http://{vm_ip}:8000/search/view" style="color: #1f6feb;">http://{vm_ip}:8000/search/view</a></p>
            <p><strong>Import:</strong> <a href="http://{vm_ip}:8000/import" style="color: #1f6feb;">http://{vm_ip}:8000/import</a></p>
        </div>
        
        <div style="background: #161b22; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2>📱 Test da Altri Dispositivi</h2>
            <p><strong>Browser:</strong> http://{vm_ip}:8000/dashboard</p>
            <p><strong>Ping:</strong> ping {vm_ip}</p>
            <p><strong>API Test:</strong> curl http://{vm_ip}:8000/api/stats</p>
        </div>
        
        <a href="/dashboard">← Torna alla Dashboard</a>
    </body>
    </html>
    """)
'''
    
    main_py_path = Path("app/main.py")
    if main_py_path.exists():
        # Crea backup
        backup_path = main_py_path.with_suffix('.py.network_backup')
        shutil.copy2(main_py_path, backup_path)
        print(f"✅ Backup creato: {backup_path}")
        
        # Aggiungi configurazione di rete
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aggiungi la configurazione di rete alla fine
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content + network_config)
        
        print(f"✅ FastAPI configurato per accesso di rete IP {vm_ip}")
        return True
    else:
        print("❌ File app/main.py non trovato")
        return False

def create_network_startup_script(vm_ip):
    """Crea script per avviare il server per accesso di rete"""
    
    script_content = f'''#!/bin/bash
# start_network_server.sh - Avvia server per accesso di rete

echo "🌐 AVVIO AI RESEARCH PLATFORM PER RETE LOCALE"
echo "=============================================="
echo "📍 IP VM: {vm_ip}"
echo "🔗 Dashboard: http://{vm_ip}:8000/dashboard"
echo "📚 API Docs: http://{vm_ip}:8000/docs"
echo "🌐 Network Info: http://{vm_ip}:8000/network-info"
echo "=============================================="

# Verifica virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔄 Attivazione virtual environment..."
    source venv/bin/activate
fi

# Installa dipendenze se necessario
echo "📦 Verifica dipendenze..."
pip install jinja2 python-multipart aiofiles pandas openpyxl --quiet

# Avvia server su tutte le interfacce di rete
echo "🚀 Avvio server FastAPI..."
echo "   Host: 0.0.0.0 (tutte le interfacce)"
echo "   Porta: 8000"
echo "   Reload: attivo"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "✅ Server terminato"
'''
    
    script_path = Path("start_network_server.sh")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Rendi eseguibile
    os.chmod(script_path, 0o755)
    
    print(f"✅ Script di avvio creato: {script_path}")
    return script_path

def create_network_info_file(vm_ip):
    """Crea file con tutte le informazioni di accesso di rete"""
    
    info_content = f"""# 🌐 AI Research Platform - Accesso di Rete

## 📍 Configurazione VM Proxmox
- **IP Virtual Machine**: `{vm_ip}`
- **Porta Server**: `8000`
- **Protocollo**: HTTP
- **Accesso**: Rete locale completa

## 🔗 URL di Accesso

### 🖥️ Interfacce Web Principali
```
Dashboard:     http://{vm_ip}:8000/dashboard
Progetti:      http://{vm_ip}:8000/projects/view
Ricerca:       http://{vm_ip}:8000/search/view
Importazione:  http://{vm_ip}:8000/import
API Docs:      http://{vm_ip}:8000/docs
Network Info:  http://{vm_ip}:8000/network-info
```

### 🔌 Endpoint API
```
Base URL:      http://{vm_ip}:8000
Statistiche:   http://{vm_ip}:8000/api/stats
Ricerca:       http://{vm_ip}:8000/search/?q=termine
Progetti:      http://{vm_ip}:8000/projects/
```

## 📱 Test di Connettività

### Da Computer nella Rete
```bash
# Test ping
ping {vm_ip}

# Test porta HTTP
telnet {vm_ip} 8000
# oppure
nc -zv {vm_ip} 8000

# Test API
curl http://{vm_ip}:8000/api/stats
```

### Da Browser
1. **Desktop/Laptop**: http://{vm_ip}:8000/dashboard
2. **Smartphone**: http://{vm_ip}:8000/dashboard
3. **Tablet**: http://{vm_ip}:8000/dashboard

## 🚀 Avvio del Server

### Metodo 1: Script Automatico
```bash
./start_network_server.sh
```

### Metodo 2: Comando Manuale
```bash
# Attiva virtual environment
source venv/bin/activate

# Avvia server per rete
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 Risoluzione Problemi

### Se non raggiungibile dalla rete:

1. **Verifica IP VM**
   ```bash
   ip addr show
   hostname -I
   ```

2. **Controlla Firewall**
   ```bash
   sudo ufw status
   sudo ufw allow 8000/tcp
   ```

3. **Verifica Processo Server**
   ```bash
   ps aux | grep uvicorn
   netstat -tuln | grep 8000
   ```

4. **Test Locale**
   ```bash
   curl http://localhost:8000/api/stats
   curl http://127.0.0.1:8000/api/stats
   ```

### Se il frontend non carica:
- Controlla che i template esistano in `app/templates/`
- Verifica che le dipendenze siano installate: `pip install jinja2 python-multipart`
- Guarda i log del server per errori

## 🔒 Sicurezza Rete Locale

**✅ Configurazione Attuale**: Sicura per rete locale privata

**⚠️ Per Accesso Internet**: Implementare:
- HTTPS/SSL con certificati
- Autenticazione utenti
- Firewall con whitelist IP
- Rate limiting e protezione DDoS
- VPN per accesso remoto sicuro

## 📊 Monitoraggio

### Log del Server
```bash
# Visualizza log in tempo reale
tail -f logs/app.log
```

### Statistiche Sistema
```bash
# API per statistiche
curl http://{vm_ip}:8000/api/stats | python -m json.tool
```

### Controllo Risorse
```bash
# Uso CPU/RAM
htop
# Connessioni di rete
netstat -an | grep 8000
```

---

**🎉 La piattaforma è ora accessibile da tutta la rete locale!**

Generato il: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    with open("NETWORK_SETUP_INFO.md", 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print("📄 File informazioni di rete creato: NETWORK_SETUP_INFO.md")

def main():
    """Setup completo frontend + rete"""
    print("🌐 SETUP FRONTEND + ACCESSO DI RETE")
    print("=" * 50)
    
    # 1. Rileva IP VM
    vm_ip = get_vm_ip()
    print(f"📍 IP VM rilevato: {vm_ip}")
    
    # 2. Installa dipendenze
    print("\n📦 Installazione dipendenze...")
    deps = ["jinja2", "python-multipart", "aiofiles", "pandas", "openpyxl"]
    for dep in deps:
        os.system(f"pip install {dep} --quiet")
    print("✅ Dipendenze installate")
    
    # 3. Crea struttura directory
    print("\n📁 Creazione directory...")
    dirs = ["app/templates", "app/static", "app/static/css", "app/static/js"]
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Struttura directory creata")
    
    # 4. Crea template per rete
    print(f"\n🎨 Creazione template per IP {vm_ip}...")
    create_network_ready_templates(vm_ip)
    
    # 5. Aggiorna FastAPI
    print(f"\n⚙️ Configurazione FastAPI per rete...")
    if update_fastapi_for_network(vm_ip):
        print("✅ FastAPI configurato per accesso di rete")
    
    # 6. Crea script di avvio
    print(f"\n🚀 Creazione script di avvio...")
    script_path = create_network_startup_script(vm_ip)
    
    # 7. Crea file informazioni
    print(f"\n📄 Creazione documentazione...")
    create_network_info_file(vm_ip)
    
    # 8. Configura firewall (opzionale)
    print(f"\n🔥 Configurazione firewall...")
    try:
        subprocess.run(['sudo', 'ufw', 'allow', '8000/tcp'], 
                      capture_output=True, check=True)
        print("✅ Firewall configurato (porta 8000 aperta)")
    except:
        print("⚠️  Configura manualmente: sudo ufw allow 8000/tcp")
    
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETATO!")
    print("=" * 50)
    print(f"\n🌐 La piattaforma è configurata per accesso di rete!")
    print(f"📍 IP VM: {vm_ip}")
    print(f"🔗 URL Dashboard: http://{vm_ip}:8000/dashboard")
    print(f"📚 API Docs: http://{vm_ip}:8000/docs")
    
    print(f"\n🚀 Per avviare il server:")
    print(f"   ./{script_path}")
    
    print(f"\n📱 Test da altri dispositivi nella rete:")
    print(f"   Browser: http://{vm_ip}:8000/dashboard")
    print(f"   Ping: ping {vm_ip}")
    print(f"   API: curl http://{vm_ip}:8000/api/stats")
    
    print(f"\n📋 Documentazione completa: NETWORK_SETUP_INFO.md")
    print(f"📄 Script di avvio: {script_path}")
    
    print(f"\n✨ Ora tutta la rete può accedere alla piattaforma!")

if __name__ == "__main__":
    main()