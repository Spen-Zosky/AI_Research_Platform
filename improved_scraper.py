# improved_scrape_single_source.py
import sys
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from utils import api_client, web_scraper, clean_text, retry_on_failure, validate_url
from config import config

logger = logging.getLogger(__name__)

class SourceScraper:
    """Scraper avanzato per singole fonti"""
    
    def __init__(self):
        self.api = api_client
        self.scraper = web_scraper
    
    @retry_on_failure(max_attempts=3, delay=2.0)
    def get_source_info(self, source_id: int) -> Optional[Dict[str, Any]]:
        """Recupera informazioni sulla fonte dal database"""
        logger.info(f"Recupero informazioni per fonte ID: {source_id}")
        
        # Cerca in tutti i progetti
        projects = self.api.get("/projects/", params={"limit": 2000})
        if not projects:
            logger.error("Impossibile recuperare la lista dei progetti")
            return None
        
        for project in projects:
            for source in project.get('sources', []):
                if source['id'] == source_id:
                    logger.info(f"Fonte trovata: {source['title']} - {source['url']}")
                    return source
        
        logger.error(f"Fonte con ID {source_id} non trovata")
        return None
    
    def scrape_content(self, url: str) -> Optional[str]:
        """Esegue lo scraping del contenuto da una URL"""
        try:
            # Valida la URL
            validated_url = validate_url(url)
            logger.info(f"Inizio scraping di: {validated_url}")
            
            # Scarica il contenuto
            html_content = self.scraper.scrape_url(validated_url)
            if not html_content:
                return None
            
            # Pulisce il contenuto HTML
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Rimuove elementi non necessari
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Estrae il testo pulito
            text = soup.get_text()
            cleaned_text = clean_text(text)
            
            logger.info(f"Estratti {len(cleaned_text)} caratteri di testo pulito")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Errore durante lo scraping di {url}: {e}")
            return None
    
    @retry_on_failure(max_attempts=3, delay=1.0)
    def save_content(self, source_id: int, content: str) -> bool:
        """Salva il contenuto nel database"""
        logger.info(f"Salvataggio contenuto per fonte ID: {source_id}")
        
        try:
            update_data = {"content": content}
            result = self.api.put(f"/sources/{source_id}", json=update_data)
            
            if result is not None:
                logger.info("Contenuto salvato con successo nel database")
                return True
            else:
                logger.error("Errore durante il salvataggio nel database")
                return False
                
        except Exception as e:
            logger.error(f"Errore nel salvataggio: {e}")
            return False
    
    def process_source(self, source_id: int) -> bool:
        """Processa una singola fonte: recupera info, fa scraping e salva"""
        try:
            # 1. Recupera informazioni sulla fonte
            source_info = self.get_source_info(source_id)
            if not source_info:
                return False
            
            # 2. Verifica se il contenuto è già presente
            if source_info.get('content') and source_info['content'].strip():
                logger.info("Contenuto già presente per questa fonte, skip scraping")
                return True
            
            # 3. Esegue lo scraping
            url = source_info['url']
            content = self.scrape_content(url)
            
            if not content:
                logger.error("Nessun contenuto estratto dalla fonte")
                return False
            
            # 4. Salva il contenuto
            success = self.save_content(source_id, content)
            
            if success:
                logger.info(f"Fonte {source_id} processata con successo")
            else:
                logger.error(f"Errore nel processamento della fonte {source_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Errore generale nel processamento della fonte {source_id}: {e}")
            return False

def main():
    """Funzione principale"""
    if len(sys.argv) != 2:
        print("Utilizzo: python improved_scrape_single_source.py <source_id>")
        sys.exit(1)
    
    try:
        source_id = int(sys.argv[1])
    except ValueError:
        logger.error("Source ID deve essere un numero intero")
        sys.exit(1)
    
    # Verifica connessione API
    if not api_client.check_health():
        logger.error("API non raggiungibile. Assicurati che il server sia in esecuzione.")
        sys.exit(1)
    
    # Crea il scraper e processa la fonte
    scraper = SourceScraper()
    
    logger.info(f"=== Inizio processamento fonte ID: {source_id} ===")
    success = scraper.process_source(source_id)
    
    if success:
        logger.info(f"=== Fonte {source_id} processata con successo ===")
        sys.exit(0)
    else:
        logger.error(f"=== Errore nel processamento della fonte {source_id} ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
