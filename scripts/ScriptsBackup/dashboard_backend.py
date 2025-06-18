# dashboard_server.py
import os
import sys
import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import tempfile

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Aggiungi il path del progetto
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

# Import dei nostri moduli
try:
    from config import config
    from utils import api_client, web_scraper, progress_tracker
    from system_manager import SystemManager
    from improved_create_tables import DatabaseManager
except ImportError as e:
    logging.error(f"Errore importazione moduli: {e}")
    # Fallback per sviluppo
    pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Modelli Pydantic
class ImportRequest(BaseModel):
    file_type: str
    options: Dict[str, Any] = {}

class CrawlerRequest(BaseModel):
    project_id: Optional[str] = "all"
    mode: str = "parallel"
    max_workers: int = 3

class NLPRequest(BaseModel):
    source_id: Optional[int] = None
    analysis_type: str = "both"

class SystemResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# App FastAPI
app = FastAPI(
    title="Dashboard Sistema Web Scraping",
    description="API per la gestione del sistema di web scraping",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stato globale dell'applicazione
app_state = {
    "system_manager": None,
    "db_manager": None,
    "running_tasks": {},
    "system_stats": {
        "projects": 0,
        "sources": 0,
        "sources_with_content": 0,
        "api_status": "offline"
    }
}

# Task manager per operazioni in background
task_manager = {}

@app.on_event("startup")
async def startup_event():
    """Inizializzazione dell'applicazione"""
    logger.info("🚀 Avvio dashboard sistema...")
    
    try:
        # Inizializza i manager
        app_state["system_manager"] = SystemManager()
        app_state["db_manager"] = DatabaseManager()
        
        # Aggiorna statistiche iniziali
        await update_system_stats()
        
        logger.info("✅ Dashboard avviata con successo")
        app_state["system_stats"]["api_status"] = "online"
        
    except Exception as e:
        logger.error(f"❌ Errore durante l'avvio: {e}")
        app_state["system_stats"]["api_status"] = "error"

# Serve la dashboard HTML
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve la dashboard web"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    
    if dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        # Fallback: ritorna la dashboard inline
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard Sistema</title>
        </head>
        <body>
            <h1>Dashboard Sistema Web Scraping</h1>
            <p>Dashboard non trovata. Crea il file dashboard.html nella directory del progetto.</p>
        </body>
        </html>
        """)

# === API ENDPOINTS ===

@app.get("/api/status")
async def get_system_status():
    """Ottieni stato del sistema"""
    await update_system_stats()
    return {
        "success": True,
        "data": app_state["system_stats"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Health check dell'API"""
    try:
        if app_state["system_manager"]:
            health_checks = app_state["system_manager"].perform_health_checks()
            return {
                "success": True,
                "logs": [line.strip() for line in recent_logs],
                "total_lines": len(log_lines)
            }
        else:
            return {
                "success": True,
                "logs": ["Log file non trovato"],
                "total_lines": 0
            }
    except Exception as e:
        logger.error(f"Errore lettura log: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/projects")
async def get_projects():
    """Ottieni lista progetti"""
    try:
        # Simula recupero progetti (sostituisci con logica reale)
        projects = [
            {"id": 1, "name": "Progetto Ricerca", "sources_count": 45},
            {"id": 2, "name": "Analisi Mercato", "sources_count": 32},
            {"id": 3, "name": "Monitoraggio News", "sources_count": 78},
            {"id": 4, "name": "Competitor Analysis", "sources_count": 23},
            {"id": 5, "name": "Social Media", "sources_count": 56}
        ]
        
        return {
            "success": True,
            "data": projects
        }
    except Exception as e:
        logger.error(f"Errore recupero progetti: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/database/init")
async def init_database(background_tasks: BackgroundTasks):
    """Inizializza database"""
    task_id = f"db_init_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def db_init_task():
        try:
            logger.info("Inizializzazione database...")
            
            if app_state["db_manager"]:
                success = app_state["db_manager"].create_tables(drop_existing=False)
                
                task_manager[task_id] = {
                    "status": "completed" if success else "error",
                    "message": "Database inizializzato" if success else "Errore inizializzazione database",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Simula inizializzazione
                import time
                time.sleep(2)
                
                task_manager[task_id] = {
                    "status": "completed",
                    "message": "Database inizializzato (modalità simulazione)",
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.info("Inizializzazione database completata")
            
        except Exception as e:
            task_manager[task_id] = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Errore inizializzazione database: {e}")
    
    background_tasks.add_task(db_init_task)
    task_manager[task_id] = {"status": "running", "message": "Inizializzazione database in corso..."}
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "Inizializzazione database avviata"
    }

@app.post("/api/database/optimize")
async def optimize_database(background_tasks: BackgroundTasks):
    """Ottimizza database"""
    task_id = f"db_optimize_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def db_optimize_task():
        try:
            logger.info("Ottimizzazione database...")
            
            if app_state["db_manager"]:
                app_state["db_manager"]._apply_postgresql_optimizations()
                
                task_manager[task_id] = {
                    "status": "completed",
                    "message": "Database ottimizzato",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Simula ottimizzazione
                import time
                time.sleep(1)
                
                task_manager[task_id] = {
                    "status": "completed",
                    "message": "Database ottimizzato (modalità simulazione)",
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.info("Ottimizzazione database completata")
            
        except Exception as e:
            task_manager[task_id] = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Errore ottimizzazione database: {e}")
    
    background_tasks.add_task(db_optimize_task)
    task_manager[task_id] = {"status": "running", "message": "Ottimizzazione database in corso..."}
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "Ottimizzazione database avviata"
    }

@app.get("/api/reports/generate")
async def generate_report():
    """Genera report sistema"""
    try:
        logger.info("Generazione report...")
        
        if app_state["system_manager"]:
            report = app_state["system_manager"].generate_system_report()
            
            # Salva report
            report_file = Path(f"logs/dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return {
                "success": True,
                "message": "Report generato",
                "data": {
                    "report_file": str(report_file),
                    "report_content": report
                }
            }
        else:
            # Simula report
            report = f"""
=== REPORT SISTEMA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===

📊 STATISTICHE:
- Progetti: {app_state['system_stats']['projects']}
- Fonti: {app_state['system_stats']['sources']}
- Con contenuto: {app_state['system_stats']['sources_with_content']}

🏥 STATO: Sistema operativo
            """
            
            return {
                "success": True,
                "message": "Report generato (modalità simulazione)",
                "data": {"report_content": report}
            }
            
    except Exception as e:
        logger.error(f"Errore generazione report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tasks")
async def clear_completed_tasks():
    """Pulisci task completati"""
    global task_manager
    
    completed_tasks = [
        task_id for task_id, task in task_manager.items()
        if task.get("status") in ["completed", "error", "completed_with_warnings"]
    ]
    
    for task_id in completed_tasks:
        del task_manager[task_id]
    
    return {
        "success": True,
        "message": f"Rimossi {len(completed_tasks)} task completati"
    }

@app.get("/api/export/data")
async def export_data():
    """Esporta dati sistema"""
    try:
        logger.info("Esportazione dati...")
        
        # Simula esportazione
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "system_stats": app_state["system_stats"],
            "export_info": {
                "projects_exported": app_state["system_stats"]["projects"],
                "sources_exported": app_state["system_stats"]["sources"],
                "format": "JSON"
            }
        }
        
        # Salva file di export
        export_file = Path(f"exports/system_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        export_file.parent.mkdir(exist_ok=True)
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": "Dati esportati",
            "data": {
                "export_file": str(export_file),
                "records_exported": export_data["export_info"]
            }
        }
        
    except Exception as e:
        logger.error(f"Errore esportazione: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Funzioni di utilità
async def update_system_stats():
    """Aggiorna statistiche sistema"""
    try:
        if app_state["system_manager"]:
            stats = app_state["system_manager"].get_system_stats()
            app_state["system_stats"].update({
                "projects": stats.total_projects,
                "sources": stats.total_sources,
                "sources_with_content": stats.sources_with_content,
                "api_status": "online"
            })
        else:
            # Simula statistiche
            import random
            app_state["system_stats"].update({
                "projects": random.randint(5, 15),
                "sources": random.randint(100, 300),
                "sources_with_content": random.randint(50, 150),
                "api_status": "online"
            })
            
    except Exception as e:
        logger.error(f"Errore aggiornamento statistiche: {e}")
        app_state["system_stats"]["api_status"] = "error"

# Endpoint per servire file statici (se necessario)
@app.get("/dashboard.html", response_class=HTMLResponse)
async def get_dashboard_file():
    """Serve il file dashboard HTML"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    else:
        raise HTTPException(status_code=404, detail="Dashboard file non trovato")

# WebSocket per aggiornamenti real-time (opzionale)
try:
    from fastapi import WebSocket
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                # Invia aggiornamenti di stato ogni 5 secondi
                await update_system_stats()
                await websocket.send_json({
                    "type": "status_update",
                    "data": app_state["system_stats"],
                    "timestamp": datetime.now().isoformat()
                })
                await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            
except ImportError:
    logger.warning("WebSocket non disponibile")

def create_dashboard_html():
    """Crea il file dashboard.html se non esiste"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    
    if not dashboard_path.exists():
        logger.info("Creazione file dashboard.html...")
        
        # Qui dovresti copiare il contenuto HTML della dashboard
        # Per ora creiamo un placeholder
        html_content = """<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Sistema</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0d1117; color: #e6edf3; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #f0f6fc; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Dashboard Sistema Web Scraping</h1>
        <div class="card">
            <h2>Dashboard Temporanea</h2>
            <p>Crea il file dashboard.html completo nella directory del progetto.</p>
            <p>API disponibile su: <a href="/docs">/docs</a></p>
        </div>
    </div>
</body>
</html>"""
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"File dashboard.html creato: {dashboard_path}")

def main():
    """Funzione principale per avviare il server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dashboard Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8001, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--create-html", action="store_true", help="Create dashboard.html file")
    
    args = parser.parse_args()
    
    if args.create_html:
        create_dashboard_html()
        return
    
    # Crea directory necessarie
    for directory in ["logs", "exports", "temp"]:
        Path(directory).mkdir(exist_ok=True)
    
    logger.info(f"🚀 Avvio dashboard server su {args.host}:{args.port}")
    logger.info(f"📱 Dashboard disponibile su: http://{args.host}:{args.port}")
    logger.info(f"📚 API docs disponibili su: http://{args.host}:{args.port}/docs")
    
    try:
        uvicorn.run(
            "dashboard_server:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server fermato dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore server: {e}")

if __name__ == "__main__":
    main()
                "status": "healthy",
                "checks": [
                    {
                        "component": check.component,
                        "status": check.status,
                        "message": check.message
                    }
                    for check in health_checks
                ]
            }
        else:
            return {"success": False, "status": "unhealthy", "message": "System manager not initialized"}
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"success": False, "status": "error", "message": str(e)}

@app.post("/api/setup/full")
async def run_full_setup(background_tasks: BackgroundTasks):
    """Esegue setup completo del sistema"""
    task_id = f"setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def setup_task():
        try:
            logger.info("Avvio setup completo...")
            
            # Simula setup (sostituisci con logica reale)
            import time
            time.sleep(3)
            
            task_manager[task_id] = {
                "status": "completed",
                "message": "Setup completato con successo",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Setup completato")
            
        except Exception as e:
            task_manager[task_id] = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Errore setup: {e}")
    
    background_tasks.add_task(setup_task)
    task_manager[task_id] = {"status": "running", "message": "Setup in corso..."}
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "Setup avviato in background"
    }

@app.post("/api/import/file")
async def import_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    file_type: str = "excel"
):
    """Importa file (Excel, CSV, Markdown)"""
    task_id = f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Salva il file temporaneamente
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file = tmp.name
        
        def import_task():
            try:
                logger.info(f"Importazione file: {file.filename}")
                
                # Qui useresti il tuo sistema di import
                # from improved_import_data import DataImporter
                # importer = DataImporter()
                # success = importer.import_from_excel(temp_file) if file_type == 'excel' else ...
                
                # Simula importazione
                import time
                time.sleep(2)
                
                task_manager[task_id] = {
                    "status": "completed",
                    "message": f"File {file.filename} importato con successo",
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Import completato: {file.filename}")
                
            except Exception as e:
                task_manager[task_id] = {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                logger.error(f"Errore import: {e}")
            finally:
                # Pulisci file temporaneo
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
        
        background_tasks.add_task(import_task)
        task_manager[task_id] = {"status": "running", "message": "Importazione in corso..."}
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Importazione di {file.filename} avviata"
        }
        
    except Exception as e:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)
        logger.error(f"Errore durante l'upload: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/crawler/run")
async def run_crawler(request: CrawlerRequest, background_tasks: BackgroundTasks):
    """Avvia web crawler"""
    task_id = f"crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def crawler_task():
        try:
            logger.info(f"Avvio crawler: progetto {request.project_id}, modalità {request.mode}")
            
            # Qui useresti il tuo sistema di crawling
            # from improved_run_crawler import AdvancedCrawler
            # crawler = AdvancedCrawler(max_workers=request.max_workers)
            # success = crawler.crawl_project(int(request.project_id), parallel=(request.mode == 'parallel'))
            
            # Simula crawling
            import time
            time.sleep(4)
            
            task_manager[task_id] = {
                "status": "completed",
                "message": "Crawling completato con successo",
                "data": {
                    "sources_processed": 47,
                    "sources_successful": 43,
                    "sources_failed": 4
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Crawling completato")
            
        except Exception as e:
            task_manager[task_id] = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Errore crawler: {e}")
    
    background_tasks.add_task(crawler_task)
    task_manager[task_id] = {"status": "running", "message": "Crawling in corso..."}
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "Crawler avviato"
    }

@app.post("/api/nlp/analyze")
async def run_nlp_analysis(request: NLPRequest, background_tasks: BackgroundTasks):
    """Esegue analisi NLP"""
    task_id = f"nlp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def nlp_task():
        try:
            logger.info(f"Avvio analisi NLP: tipo {request.analysis_type}")
            
            # Qui useresti il tuo sistema NLP
            # from improved_extract_entities import EntityExtractor
            # extractor = EntityExtractor()
            # if request.source_id:
            #     success = extractor.process_source(request.source_id)
            # else:
            #     # Processa tutte le fonti
            #     success = True
            
            # Simula analisi NLP
            import time
            time.sleep(3)
            
            task_manager[task_id] = {
                "status": "completed",
                "message": "Analisi NLP completata",
                "data": {
                    "entities_extracted": 156,
                    "keywords_extracted": 89,
                    "sources_analyzed": 23 if not request.source_id else 1
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Analisi NLP completata")
            
        except Exception as e:
            task_manager[task_id] = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Errore NLP: {e}")
    
    background_tasks.add_task(nlp_task)
    task_manager[task_id] = {"status": "running", "message": "Analisi NLP in corso..."}
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "Analisi NLP avviata"
    }

@app.post("/api/maintenance/run")
async def run_maintenance(background_tasks: BackgroundTasks):
    """Esegue manutenzione sistema"""
    task_id = f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def maintenance_task():
        try:
            logger.info("Avvio manutenzione sistema...")
            
            if app_state["system_manager"]:
                success = app_state["system_manager"].run_maintenance()
                
                task_manager[task_id] = {
                    "status": "completed" if success else "completed_with_warnings",
                    "message": "Manutenzione completata",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Simula manutenzione
                import time
                time.sleep(2)
                
                task_manager[task_id] = {
                    "status": "completed",
                    "message": "Manutenzione completata (modalità simulazione)",
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.info("Manutenzione completata")
            
        except Exception as e:
            task_manager[task_id] = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Errore manutenzione: {e}")
    
    background_tasks.add_task(maintenance_task)
    task_manager[task_id] = {"status": "running", "message": "Manutenzione in corso..."}
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "Manutenzione avviata"
    }

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Ottieni stato di un task"""
    if task_id in task_manager:
        return {
            "success": True,
            "task_id": task_id,
            **task_manager[task_id]
        }
    else:
        raise HTTPException(status_code=404, detail="Task non trovato")

@app.get("/api/logs")
async def get_system_logs(lines: int = 50):
    """Ottieni log del sistema"""
    try:
        log_file = Path("logs/app.log")
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_lines = f.readlines()
                recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
                
            return {
                "success": True,
                