# config.py
import os
import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class ScrapingConfig:
    """Configurazione per le operazioni di scraping"""
    timeout: int = 15
    retry_attempts: int = 3
    retry_delay: float = 2.0
    rate_limit_delay: float = 2.0
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    max_content_length: int = 5_000_000  # 5MB max per pagina

@dataclass
class DatabaseConfig:
    """Configurazione per il database"""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30

@dataclass
class APIConfig:
    """Configurazione per l'API"""
    base_url: str = "http://127.0.0.1:8000"
    timeout: int = 30
    max_retries: int = 3

@dataclass
class LoggingConfig:
    """Configurazione per il logging"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None

class Config:
    """Configurazione principale dell'applicazione"""
    
    def __init__(self):
        load_dotenv()
        
        # Configurazioni principali
        self.scraping = ScrapingConfig(
            timeout=int(os.getenv("SCRAPING_TIMEOUT", "15")),
            retry_attempts=int(os.getenv("SCRAPING_RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("SCRAPING_RETRY_DELAY", "2.0")),
            rate_limit_delay=float(os.getenv("SCRAPING_RATE_LIMIT", "2.0")),
            user_agent=os.getenv("SCRAPING_USER_AGENT", ScrapingConfig.user_agent),
            max_content_length=int(os.getenv("SCRAPING_MAX_CONTENT_LENGTH", "5000000"))
        )
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL non trovato nelle variabili d'ambiente")
            
        self.database = DatabaseConfig(
            url=database_url,
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30"))
        )
        
        self.api = APIConfig(
            base_url=os.getenv("API_BASE_URL", "http://127.0.0.1:8000"),
            timeout=int(os.getenv("API_TIMEOUT", "30")),
            max_retries=int(os.getenv("API_MAX_RETRIES", "3"))
        )
        
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", LoggingConfig.format),
            file_path=os.getenv("LOG_FILE_PATH")
        )
        
        # Inizializza il logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura il sistema di logging"""
        logging.basicConfig(
            level=getattr(logging, self.logging.level.upper()),
            format=self.logging.format,
            handlers=[
                logging.StreamHandler(),
                *([logging.FileHandler(self.logging.file_path)] if self.logging.file_path else [])
            ]
        )

# Istanza globale della configurazione
config = Config()

# Esempio di file .env da creare
ENV_TEMPLATE = """
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API Configuration
API_BASE_URL=http://127.0.0.1:8000
API_TIMEOUT=30
API_MAX_RETRIES=3

# Scraping Configuration
SCRAPING_TIMEOUT=15
SCRAPING_RETRY_ATTEMPTS=3
SCRAPING_RETRY_DELAY=2.0
SCRAPING_RATE_LIMIT=2.0
SCRAPING_MAX_CONTENT_LENGTH=5000000
SCRAPING_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Database Pool Configuration
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/app.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""

def create_env_template():
    """Crea un file .env template se non esiste"""
    if not os.path.exists('.env'):
        with open('.env.template', 'w') as f:
            f.write(ENV_TEMPLATE.strip())
        print("File .env.template creato. Copialo in .env e modifica i valori secondo le tue necessità.")

if __name__ == "__main__":
    create_env_template()
