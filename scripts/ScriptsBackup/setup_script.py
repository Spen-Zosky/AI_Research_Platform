# setup_system.py
import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import shutil

# Setup logging per il setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SETUP - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemSetup:
    """Setup automatico completo del sistema"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.requirements_installed = False
        self.database_initialized = False
        self.config_created = False
        
    def check_python_version(self) -> bool:
        """Verifica che la versione di Python sia supportata"""
        logger.info("Controllo versione Python...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error(f"Python 3.8+ richiesto, trovato {version.major}.{version.minor}")
            return False
        
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} OK")
        return True
    
    def check_system_dependencies(self) -> List[str]:
        """Controlla le dipendenze di sistema"""
        logger.info("Controllo dipendenze di sistema...")
        
        missing_deps = []
        
        # Controlla PostgreSQL client
        if not shutil.which('psql'):
            missing_deps.append('postgresql-client')
        
        # Controlla git
        if not shutil.which('git'):
            missing_deps.append('git')
        
        # Controlla curl
        if not shutil.which('curl'):
            missing_deps.append('curl')
        
        if missing_deps:
            logger.warning(f"Dipendenze mancanti: {', '.join(missing_deps)}")
        else:
            logger.info("✅ Tutte le dipendenze di sistema sono presenti")
        
        return missing_deps
    
    def create_directory_structure(self) -> bool:
        """Crea la struttura di directory necessaria"""
        logger.info("Creazione struttura directory...")
        
        directories = [
            'logs',
            'data',
            'backups',
            'temp',
            'exports'
        ]
        
        try:
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(exist_ok=True)
                logger.debug(f"Directory creata/verificata: {directory}")
            
            # Crea file .gitkeep per directory vuote
            for directory in directories:
                gitkeep_path = self.project_root / directory / '.gitkeep'
                if not gitkeep_path.exists():
                    gitkeep_path.touch()
            
            logger.info("✅ Struttura directory creata")
            return True
            
        except Exception as e:
            logger.error(f"Errore nella creazione directory: {e}")
            return False
    
    def install_python_dependencies(self) -> bool:
        """Installa le dipendenze Python"""
        logger.info("Installazione dipendenze Python...")
        
        # Lista delle dipendenze principali
        requirements = [
            'fastapi>=0.104.0',
            'uvicorn[standard]>=0.24.0',
            'sqlalchemy>=2.0.0',
            'psycopg2-binary>=2.9.0',
            'requests>=2.31.0',
            'beautifulsoup4>=4.12.0',
            'lxml>=4.9.0',
            'pandas>=2.0.0',
            'openpyxl>=3.1.0',
            'spacy>=3.7.0',
            'python-dotenv>=1.0.0',
            'python-multipart>=0.0.6',
            'aiofiles>=23.0.0'
        ]
        
        try:
            # Aggiorna pip
            logger.info("Aggiornamento pip...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                          check=True, capture_output=True)
            
            # Installa dipendenze
            logger.info("Installazione pacchetti Python...")
            for requirement in requirements:
                logger.info(f"Installazione: {requirement}")
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', requirement], 
                                      capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.warning(f"Errore nell'installazione di {requirement}: {result.stderr}")
                else:
                    logger.debug(f"✅ {requirement} installato")
            
            # Installa modello spaCy
            logger.info("Installazione modello spaCy italiano...")
            subprocess.run([sys.executable, '-m', 'spacy', 'download', 'it_core_news_lg'], 
                          check=True, capture_output=True)
            
            logger.info("✅ Dipendenze Python installate")
            self.requirements_installed = True
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Errore nell'installazione dipendenze: {e}")
            return False
        except Exception as e:
            logger.error(f"Errore generico nell'installazione: {e}")
            return False
    
    def create_configuration_files(self) -> bool:
        """Crea i file di configurazione"""
        logger.info("Creazione file di configurazione...")
        
        try:
            # Crea .env se non esiste
            env_path = self.project_root / '.env'
            env_template_path = self.project_root / '.env.template'
            
            if not env_path.exists():
                if env_template_path.exists():
                    # Copia dal template
                    shutil.copy2(env_template_path, env_path)
                    logger.info("✅ File .env creato da template")
                else:
                    # Crea .env di base
                    env_content = self._generate_basic_env_content()
                    with open(env_path, 'w') as f:
                        f.write(env_content)
                    logger.info("✅ File .env di base creato")
                
                self.config_created = True
            else:
                logger.info("File .env già esistente")
            
            # Crea file di logging configuration
            self._create_logging_config()
            
            # Crea gitignore se non esiste
            self._create_gitignore()
            
            return True
            
        except Exception as e:
            logger.error(f"Errore nella creazione file di configurazione: {e}")
            return False
    
    def _generate_basic_env_content(self) -> str:
        """Genera contenuto .env di base"""
        return '''# Configurazione Database
DATABASE_URL=postgresql://user:password@localhost:5432/scraping_db

# Configurazione API
API_BASE_URL=http://127.0.0.1:8000
API_TIMEOUT=30
API_MAX_RETRIES=3

# Configurazione Scraping
SCRAPING_TIMEOUT=15
SCRAPING_RETRY_ATTEMPTS=3
SCRAPING_RETRY_DELAY=2.0
SCRAPING_RATE_LIMIT=2.0
SCRAPING_MAX_CONTENT_LENGTH=5000000

# Configurazione Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/app.log

# Configurazione Sistema
MAX_CRAWLER_WORKERS=3
ENVIRONMENT=development
DEBUG=false
'''
    
    def _create_logging_config(self):
        """Crea configurazione per il logging"""
        logging_config = '''
# logging.conf
[loggers]
keys=root,scraper,api,system

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler,fileHandler

[logger_scraper]
level=INFO
handlers=consoleHandler,fileHandler
qualname=scraper
propagate=0

[logger_api]
level=INFO
handlers=consoleHandler,fileHandler
qualname=api
propagate=0

[logger_system]
level=INFO
handlers=consoleHandler,fileHandler
qualname=system
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=detailedFormatter
args=('logs/app.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s
'''
        
        config_path = self.project_root / 'logging.conf'
        with open(config_path, 'w') as f:
            f.write(logging_config.strip())
    
    def _create_gitignore(self):
        """Crea file .gitignore"""
        gitignore_content = '''# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# Logs
logs/
*.log

# Data files
data/
temp/
backups/
exports/

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
'''
        
        gitignore_path = self.project_root / '.gitignore'
        if not gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            logger.info("✅ File .gitignore creato")
    
    def check_database_connection(self) -> bool:
        """Verifica la connessione al database"""
        logger.info("Verifica connessione database...")
        
        try:
            # Importa e usa il sistema di config
            from config import config
            from sqlalchemy import create_engine, text
            
            engine = create_engine(config.database.url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✅ Connessione database OK")
            return True
            
        except ImportError:
            logger.warning("Moduli non ancora disponibili, salto controllo database")
            return True
        except Exception as e:
            logger.error(f"Errore connessione database: {e}")
            logger.info("💡 Assicurati che PostgreSQL sia installato e in esecuzione")
            logger.info("💡 Verifica le credenziali nel file .env")
            return False
    
    def initialize_database(self) -> bool:
        """Inizializza il database"""
        logger.info("Inizializzazione database...")
        
        try:
            # Prova a importare e usare il setup database
            sys.path.insert(0, str(self.project_root))
            from improved_create_tables import DatabaseManager
            
            db_manager = DatabaseManager()
            if db_manager.test_connection():
                success = db_manager.create_tables(drop_existing=False)
                if success:
                    logger.info("✅ Database inizializzato")
                    self.database_initialized = True
                    return True
                else:
                    logger.error("Errore nell'inizializzazione database")
                    return False
            else:
                logger.error("Impossibile connettersi al database")
                return False
                
        except ImportError as e:
            logger.warning(f"Impossibile importare moduli database: {e}")
            return False
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione database: {e}")
            return False
    
    def run_post_setup_tests(self) -> bool:
        """Esegue test post-setup"""
        logger.info("Esecuzione test post-setup...")
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Import dei moduli principali
        total_tests += 1
        try:
            from config import config
            from utils import api_client
            tests_passed += 1
            logger.info("✅ Import moduli principali OK")
        except Exception as e:
            logger.error(f"❌ Errore import moduli: {e}")
        
        # Test 2: Configurazione
        total_tests += 1
        try:
            from config import config
            if config.database.url and config.api.base_url:
                tests_passed += 1
                logger.info("✅ Configurazione caricata OK")
        except Exception as e:
            logger.error(f"❌ Errore configurazione: {e}")
        
        # Test 3: Directory structure
        total_tests += 1
        required_dirs = ['logs', 'data', 'backups']
        if all((self.project_root / d).exists() for d in required_dirs):
            tests_passed += 1
            logger.info("✅ Struttura directory OK")
        else:
            logger.error("❌ Struttura directory incompleta")
        
        success_rate = tests_passed / total_tests
        logger.info(f"Test completati: {tests_passed}/{total_tests} ({success_rate:.0%})")
        
        return success_rate >= 0.8
    
    def generate_setup_report(self) -> str:
        """Genera report del setup"""
        report_lines = [
            "=" * 60,
            "REPORT SETUP SISTEMA",
            "=" * 60,
            "",
            f"📁 Directory progetto: {self.project_root}",
            f"🐍 Python: {sys.version.split()[0]}",
            "",
            "📋 COMPONENTI INSTALLATI:",
            f"  {'✅' if self.requirements_installed else '❌'} Dipendenze Python",
            f"  {'✅' if self.config_created else '❌'} File di configurazione",
            f"  {'✅' if self.database_initialized else '❌'} Database",
            "",
            "🔧 PROSSIMI PASSI:",
        ]
        
        if not self.config_created:
            report_lines.append("  1. Configura il file .env con le tue impostazioni")
        
        if not self.database_initialized:
            report_lines.append("  2. Configura PostgreSQL e inizializza il database")
        
        report_lines.extend([
            "  3. Avvia l'API: python -m app.main",
            "  4. Importa dati: python improved_import_data.py",
            "  5. Esegui crawling: python improved_run_crawler.py",
            "",
            "📚 DOCUMENTAZIONE:",
            "  - File README.md per istruzioni dettagliate",
            "  - File .env.template per esempi di configurazione",
            "  - Directory logs/ per i file di log",
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def run_full_setup(self) -> bool:
        """Esegue setup completo del sistema"""
        logger.info("🚀 INIZIO SETUP SISTEMA COMPLETO")
        logger.info("=" * 50)
        
        setup_success = True
        
        # Step 1: Controllo requisiti
        if not self.check_python_version():
            return False
        
        missing_deps = self.check_system_dependencies()
        if missing_deps:
            logger.warning(f"Dipendenze mancanti: {missing_deps}")
            logger.info("Installa le dipendenze e rilancia il setup")
        
        # Step 2: Struttura directory
        if not self.create_directory_structure():
            setup_success = False
        
        # Step 3: Configurazione
        if not self.create_configuration_files():
            setup_success = False
        
        # Step 4: Dipendenze Python
        install_deps = input("\nInstallare dipendenze Python? (s/n): ").lower()
        if install_deps in ['s', 'si', 'y', 'yes']:
            if not self.install_python_dependencies():
                setup_success = False
        
        # Step 5: Database
        if self.requirements_installed:
            setup_db = input("Inizializzare database? (s/n): ").lower()
            if setup_db in ['s', 'si', 'y', 'yes']:
                if self.check_database_connection():
                    self.initialize_database()
        
        # Step 6: Test finali
        if self.requirements_installed:
            if not self.run_post_setup_tests():
                setup_success = False
        
        # Report finale
        report = self.generate_setup_report()
        print("\n" + report)
        
        # Salva report
        report_file = self.project_root / 'logs' / 'setup_report.txt'
        try:
            with open(report_file, 'w') as f:
                f.write(report)
            logger.info(f"Report salvato in: {report_file}")
        except Exception as e:
            logger.warning(f"Impossibile salvare report: {e}")
        
        if setup_success:
            logger.info("🎉 SETUP COMPLETATO CON SUCCESSO!")
        else:
            logger.warning("⚠️  Setup completato con alcuni problemi")
        
        return setup_success

class InteractiveSetup:
    """Setup interattivo guidato"""
    
    def __init__(self):
        self.setup = SystemSetup()
    
    def welcome_message(self):
        """Messaggio di benvenuto"""
        print("""
🔧 SETUP SISTEMA DI WEB SCRAPING E ANALISI CONTENUTI
====================================================

Questo script configurerà automaticamente il sistema con:
- Installazione dipendenze Python
- Configurazione database
- Creazione struttura directory
- File di configurazione
- Test del sistema

Assicurati di avere:
✓ Python 3.8+
✓ PostgreSQL installato e attivo
✓ Connessione internet per scaricare dipendenze

====================================================
        """)
    
    def run_interactive_setup(self):
        """Esegue setup interattivo"""
        self.welcome_message()
        
        proceed = input("Procedere con il setup? (s/n): ").lower()
        if proceed not in ['s', 'si', 'y', 'yes']:
            print("Setup annullato.")
            return False
        
        try:
            success = self.setup.run_full_setup()
            
            if success:
                print("\n🎉 Setup completato! Il sistema è pronto all'uso.")
                print("\nPer iniziare:")
                print("1. python -m app.main  # Avvia l'API")
                print("2. python improved_import_data.py  # Importa dati")
            else:
                print("\n⚠️  Setup completato con problemi. Controlla i log.")
            
            return success
            
        except KeyboardInterrupt:
            print("\n\nSetup interrotto dall'utente.")
            return False
        except Exception as e:
            logger.error(f"Errore durante setup: {e}")
            return False

def main():
    """Funzione principale"""
    try:
        if len(sys.argv) == 1:
            # Modalità interattiva
            interactive_setup = InteractiveSetup()
            success = interactive_setup.run_interactive_setup()
            sys.exit(0 if success else 1)
        
        elif len(sys.argv) == 2:
            # Modalità comando
            command = sys.argv[1].lower()
            setup = SystemSetup()
            
            if command == 'check':
                # Solo controlli
                setup.check_python_version()
                setup.check_system_dependencies()
                setup.check_database_connection()
            
            elif command == 'install':
                # Solo installazione dipendenze
                setup.install_python_dependencies()
            
            elif command == 'config':
                # Solo configurazione
                setup.create_configuration_files()
            
            elif command == 'database':
                # Solo database
                setup.initialize_database()
            
            elif command == 'full':
                # Setup completo non interattivo
                success = setup.run_full_setup()
                sys.exit(0 if success else 1)
            
            else:
                print("Comandi disponibili:")
                print("  check     - Solo controlli sistema")
                print("  install   - Solo installazione dipendenze")
                print("  config    - Solo configurazione")
                print("  database  - Solo inizializzazione database")
                print("  full      - Setup completo non interattivo")
        
        else:
            print("Utilizzo:")
            print("  python setup_system.py           # Setup interattivo")
            print("  python setup_system.py [comando] # Comando specifico")
    
    except Exception as e:
        logger.error(f"Errore inaspettato: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()