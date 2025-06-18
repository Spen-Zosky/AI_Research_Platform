# run_dashboard.py
import os
import sys
import webbrowser
import time
import subprocess
import logging
from pathlib import Path
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - DASHBOARD - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DashboardLauncher:
    """Launcher per la dashboard con controlli e setup automatico"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.dashboard_html_path = self.project_root / "dashboard.html"
        self.server_script = self.project_root / "dashboard_server.py"
        
    def check_dependencies(self) -> bool:
        """Verifica le dipendenze necessarie"""
        logger.info("🔍 Controllo dipendenze...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "python-multipart"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                logger.debug(f"✅ {package} disponibile")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"❌ {package} mancante")
        
        if missing_packages:
            logger.error(f"Pacchetti mancanti: {', '.join(missing_packages)}")
            logger.info("Installa con: pip install " + " ".join(missing_packages))
            return False
        
        logger.info("✅ Tutte le dipendenze sono disponibili")
        return True
    
    def create_dashboard_html(self) -> bool:
        """Crea il file dashboard.html dalla dashboard web"""
        logger.info("📄 Creazione file dashboard.html...")
        
        try:
            # Qui dovremmo copiare il contenuto HTML della dashboard dal nostro artifact
            # Per ora creiamo una versione che punta al server
            html_content = '''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Sistema Web Scraping</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #e6edf3;
            line-height: 1.5;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }

        .container {
            text-align: center;
            max-width: 600px;
            padding: 40px;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
        }

        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
        }

        h1 {
            font-size: 2rem;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 16px;
        }

        .subtitle {
            font-size: 1.1rem;
            color: #7d8590;
            margin-bottom: 32px;
        }

        .status {
            padding: 12px 20px;
            border-radius: 6px;
            margin: 16px 0;
            font-weight: 500;
        }

        .status.loading {
            background-color: #0f1419;
            color: #1f6feb;
            border: 1px solid #1f6feb;
        }

        .status.success {
            background-color: #0f2419;
            color: #3fb950;
            border: 1px solid #3fb950;
        }

        .status.error {
            background-color: #2b0f0f;
            color: #f85149;
            border: 1px solid #f85149;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid;
            text-decoration: none;
            margin: 8px;
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

        .loading-spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #30363d;
            border-top: 2px solid #1f6feb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .info {
            margin-top: 24px;
            padding: 16px;
            background-color: #0d1117;
            border-radius: 6px;
            font-size: 12px;
            color: #7d8590;
            text-align: left;
        }

        .info code {
            background-color: #21262d;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'SF Mono', Monaco, 'Inconsolata', 'Roboto Mono', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀</div>
        <h1>Dashboard Sistema</h1>
        <p class="subtitle">Sistema di Web Scraping e Analisi Contenuti</p>
        
        <div id="status" class="status loading">
            <div class="loading-spinner"></div>
            Connessione al server...
        </div>
        
        <div id="actions" style="display: none;">
            <a href="/api/docs" class="btn btn-primary" target="_blank">📚 API Documentation</a>
            <button class="btn btn-primary" onclick="openDashboard()">🎛️ Apri Dashboard</button>
        </div>
        
        <div class="info">
            <strong>Informazioni:</strong><br>
            • Server API: <code>http://127.0.0.1:8001</code><br>
            • Dashboard: <code>http://127.0.0.1:8001/</code><br>
            • API Docs: <code>http://127.0.0.1:8001/docs</code><br>
            • Status: <span id="server-status">Controllo...</span>
        </div>
    </div>

    <script>
        let checkInterval;
        
        async function checkServerStatus() {
            try {
                const response = await fetch('/api/status');
                if (response.ok) {
                    document.getElementById('status').className = 'status success';
                    document.getElementById('status').innerHTML = '✅ Server online e operativo';
                    document.getElementById('actions').style.display = 'block';
                    document.getElementById('server-status').textContent = 'Online';
                    
                    // Stop checking once connected
                    if (checkInterval) {
                        clearInterval(checkInterval);
                    }
                } else {
                    throw new Error('Server non raggiungibile');
                }
            } catch (error) {
                document.getElementById('status').className = 'status error';
                document.getElementById('status').innerHTML = '❌ Server non raggiungibile';
                document.getElementById('server-status').textContent = 'Offline';
            }
        }
        
        function openDashboard() {
            window.location.href = '/';
        }
        
        // Check server status every 2 seconds
        checkServerStatus();
        checkInterval = setInterval(checkServerStatus, 2000);
        
        // Try to redirect to full dashboard after 3 seconds if server is up
        setTimeout(() => {
            fetch('/api/status')
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/';
                    }
                })
                .catch(() => {
                    // Server not ready yet, keep showing this page
                });
        }, 3000);
    </script>
</body>
</html>'''
            
            with open(self.dashboard_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ File dashboard.html creato: {self.dashboard_html_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore creazione dashboard.html: {e}")
            return False
    
    def create_server_script(self) -> bool:
        """Crea il file dashboard_server.py se non esiste"""
        if self.server_script.exists():
            logger.info("✅ Script server già presente")
            return True
        
        logger.info("📄 Creazione script server...")
        
        try:
            # Qui dovremmo copiare il contenuto del server dal nostro artifact
            # Per ora creiamo un server minimale
            server_content = '''# dashboard_server.py - Generato automaticamente
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

app = FastAPI(title="Dashboard Sistema Web Scraping")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_path = Path("dashboard.html")
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    else:
        return HTMLResponse("<h1>Dashboard non trovata</h1>")

@app.get("/api/status")
async def get_status():
    return {"success": True, "status": "online", "message": "Server operativo"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
'''
            
            with open(self.server_script, 'w', encoding='utf-8') as f:
                f.write(server_content)
            
            logger.info(f"✅ Script server creato: {self.server_script}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore creazione server script: {e}")
            return False
    
    def start_server(self, host: str = "127.0.0.1", port: int = 8001, background: bool = True) -> bool:
        """Avvia il server dashboard"""
        logger.info(f"🚀 Avvio server dashboard su {host}:{port}")
        
        try:
            if background:
                # Avvia in background
                process = subprocess.Popen([
                    sys.executable, str(self.server_script),
                    "--host", host,
                    "--port", str(port)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                logger.info(f"✅ Server avviato in background (PID: {process.pid})")
                
                # Attendi che il server sia pronto
                logger.info("⏳ Attendo che il server sia pronto...")
                time.sleep(3)
                
                return True
            else:
                # Avvia in foreground
                subprocess.run([
                    sys.executable, str(self.server_script),
                    "--host", host,
                    "--port", str(port)
                ])
                return True
                
        except Exception as e:
            logger.error(f"❌ Errore avvio server: {e}")
            return False
    
    def open_browser(self, url: str):
        """Apre il browser alla dashboard"""
        logger.info(f"🌐 Apertura browser: {url}")
        try:
            webbrowser.open(url)
            logger.info("✅ Browser aperto")
        except Exception as e:
            logger.warning(f"⚠️ Impossibile aprire browser automaticamente: {e}")
            logger.info(f"🔗 Apri manualmente: {url}")
    
    def run(self, host: str = "127.0.0.1", port: int = 8001, open_browser: bool = True, background: bool = True):
        """Esegue il setup completo e avvia la dashboard"""
        logger.info("🎯 Avvio Dashboard Sistema Web Scraping")
        logger.info("=" * 50)
        
        # 1. Controllo dipendenze
        if not self.check_dependencies():
            logger.error("❌ Dipendenze mancanti. Installale e riprova.")
            return False
        
        # 2. Setup file
        if not self.dashboard_html_path.exists():
            if not self.create_dashboard_html():
                return False
        
        if not self.server_script.exists():
            if not self.create_server_script():
                return False
        
        # 3. Avvio server
        server_url = f"http://{host}:{port}"
        
        if not self.start_server(host, port, background):
            return False
        
        # 4. Apertura browser
        if open_browser:
            time.sleep(2)  # Attendi che il server sia completamente pronto
            self.open_browser(server_url)
        
        # 5. Informazioni finali
        logger.info("🎉 Dashboard avviata con successo!")
        logger.info(f"🔗 URL Dashboard: {server_url}")
        logger.info(f"📚 API Docs: {server_url}/docs")
        logger.info("🛑 Premi Ctrl+C per fermare il server")
        
        if not background:
            try:
                # Mantieni il processo attivo
                input("\nPremi INVIO per fermare il server...")
            except KeyboardInterrupt:
                logger.info("🛑 Server fermato")
        
        return True

def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(description="Launcher Dashboard Sistema Web Scraping")
    parser.add_argument("--host", default="127.0.0.1", help="Host del server (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8001, help="Porta del server (default: 8001)")
    parser.add_argument("--no-browser", action="store_true", help="Non aprire il browser automaticamente")
    parser.add_argument("--foreground", action="store_true", help="Esegui server in foreground")
    parser.add_argument("--setup-only", action="store_true", help="Solo setup file, non avviare server")
    
    args = parser.parse_args()
    
    try:
        launcher = DashboardLauncher()
        
        if args.setup_only:
            logger.info("🔧 Solo setup file...")
            launcher.create_dashboard_html()
            launcher.create_server_script()
            logger.info("✅ Setup completato")
            return
        
        success = launcher.run(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
            background=not args.foreground
        )
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Oper