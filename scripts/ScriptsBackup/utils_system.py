# utils.py
import time
import requests
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import config

logger = logging.getLogger(__name__)

class APIClient:
    """Client API con retry automatico e gestione errori avanzata"""
    
    def __init__(self):
        self.base_url = config.api.base_url
        self.session = requests.Session()
        
        # Configura retry strategy
        retry_strategy = Retry(
            total=config.api.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Timeout di default
        self.session.timeout = config.api.timeout
    
    def get(self, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """GET request con gestione errori"""
        return self._request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """POST request con gestione errori"""
        return self._request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """PUT request con gestione errori"""
        return self._request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """DELETE request con gestione errori"""
        return self._request("DELETE", endpoint, **kwargs)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """Metodo interno per gestire le richieste"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"API {method} request to {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Prova a decodificare JSON, altrimenti ritorna il testo
            try:
                return response.json()
            except ValueError:
                return {"text": response.text, "status_code": response.status_code}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API {method} request failed for {url}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            return None
    
    def check_health(self) -> bool:
        """Verifica che l'API sia raggiungibile"""
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=5)
            return response.status_code == 200
        except:
            return False

class WebScraper:
    """Scraper web con retry automatico e rate limiting"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.scraping.user_agent})
        
        # Configura retry strategy per scraping
        retry_strategy = Retry(
            total=config.scraping.retry_attempts,
            backoff_factor=config.scraping.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.last_request_time = 0
    
    def scrape_url(self, url: str) -> Optional[str]:
        """Scrape una URL con rate limiting e gestione errori"""
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < config.scraping.rate_limit_delay:
            sleep_time = config.scraping.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: attendo {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        try:
            logger.info(f"Scraping URL: {url}")
            response = self.session.get(
                url, 
                timeout=config.scraping.timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Controlla la dimensione del contenuto
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > config.scraping.max_content_length:
                logger.warning(f"Contenuto troppo grande ({content_length} bytes): {url}")
                return None
            
            # Leggi il contenuto
            content = response.text
            if len(content) > config.scraping.max_content_length:
                logger.warning(f"Contenuto troppo grande dopo il download: {url}")
                content = content[:config.scraping.max_content_length]
            
            self.last_request_time = time.time()
            logger.debug(f"Successfully scraped {len(content)} characters from {url}")
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None
        finally:
            self.last_request_time = time.time()

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, exponential_backoff: bool = True):
    """Decoratore per retry automatico di funzioni"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt if exponential_backoff else 1)
                        logger.warning(f"Tentativo {attempt + 1} fallito per {func.__name__}: {e}. Riprovo tra {wait_time}s")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Tutti i {max_attempts} tentativi falliti per {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator

def progress_tracker(total: int, description: str = "Processing"):
    """Context manager per tracking del progresso"""
    class ProgressTracker:
        def __init__(self, total: int, description: str):
            self.total = total
            self.description = description
            self.current = 0
            self.start_time = time.time()
        
        def update(self, increment: int = 1):
            self.current += increment
            elapsed = time.time() - self.start_time
            if self.current > 0:
                eta = (elapsed / self.current) * (self.total - self.current)
                percentage = (self.current / self.total) * 100
                logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%) - ETA: {eta:.0f}s")
        
        def __enter__(self):
            logger.info(f"Inizio {self.description}: {self.total} elementi")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed = time.time() - self.start_time
            logger.info(f"Completato {self.description}: {self.current}/{self.total} in {elapsed:.2f}s")
    
    return ProgressTracker(total, description)

def validate_url(url: str) -> str:
    """Valida e normalizza una URL"""
    if not url or not isinstance(url, str):
        raise ValueError("URL deve essere una stringa non vuota")
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    # Validazione base della URL
    if not any(char in url for char in ['.', '/']):
        raise ValueError(f"URL non valida: {url}")
    
    return url

def clean_text(text: str) -> str:
    """Pulisce il testo estratto da HTML"""
    if not text:
        return ""
    
    # Rimuovi spazi multipli e normalizza line breaks
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    clean_text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return clean_text

def safe_int(value: Any, default: int = 0) -> int:
    """Conversione sicura a intero"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_str(value: Any, default: str = "") -> str:
    """Conversione sicura a stringa"""
    try:
        return str(value).strip() if value is not None else default
    except:
        return default

# Istanze globali
api_client = APIClient()
web_scraper = WebScraper()
