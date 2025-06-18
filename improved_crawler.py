# improved_run_crawler.py
import sys
import logging
import time
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from bs4 import BeautifulSoup
from utils import api_client, web_scraper, clean_text, progress_tracker, retry_on_failure
from config import config

logger = logging.getLogger(__name__)

@dataclass
class CrawlResult:
    """Risultato di un'operazione di crawling"""
    source_id: int
    success: bool
    content_length: int = 0
    error: Optional[str] = None
    processing_time: float = 0.0

class AdvancedCrawler:
    """Crawler avanzato con supporto per crawling parallelo e gestione intelligente degli errori"""
    
    def __init__(self, max_workers: int = 3):
        self.api = api_client
        self.scraper = web_scraper
        self.max_workers = max_workers
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_content_length': 0
        }
    
    @retry_on_failure(max_attempts=2, delay=1.0)
    def get_all_projects(self) -> Optional[List[Dict]]:
        """Recupera tutti i progetti disponibili"""
        logger.info("Recupero lista progetti...")
        projects = self.api.get("/projects/", params={"limit": 2000})
        
        if projects:
            logger.info(f"Trovati {len(projects)} progetti")
            return projects
        else:
            logger.error("Impossibile recuperare i progetti")
            return None
    
    @retry_on_failure(max_attempts=2, delay=1.0)
    def get_sources_for_project(self, project_id: int) -> List[Dict]:
        """Recupera tutte le fonti per un progetto"""
        logger.info(f"Recupero fonti per progetto {project_id}...")
        sources = self.api.get(f"/projects/{project_id}/sources/", params={"limit": 5000})
        
        if sources:
            logger.info(f"Trovate {len(sources)} fonti per progetto {project_id}")
            return sources
        else:
            logger.warning(f"Nessuna fonte trovata per progetto {project_id}")
            return []
    
    def should_skip_source(self, source: Dict) -> bool:
        """Determina se saltare una fonte basandosi su vari criteri"""
        # Salta se il contenuto è già presente e non vuoto
        if source.get('content') and source['content'].strip():
            return True
        
        # Salta URL problematiche conosciute
        url = source.get('url', '').lower()
        problematic_patterns = [
            'javascript:', 'mailto:', 'tel:', 'ftp://',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.tar', '.gz'
        ]
        
        if any(pattern in url for pattern in problematic_patterns):
            logger.debug(f"Saltata URL problematica: {url}")
            return True
        
        return False
    
    def scrape_single_source(self, source: Dict) -> CrawlResult:
        """Scrape una singola fonte"""
        start_time = time.time()
        source_id = source['id']
        url = source['url']
        
        try:
            logger.debug(f"Scraping fonte {source_id}: {source.get('title', 'N/A')}")
            
            # Controlla se saltare
            if self.should_skip_source(source):
                self.stats['skipped'] += 1
                return CrawlResult(
                    source_id=source_id,
                    success=True,  # È un successo saltare contenuto già presente
                    processing_time=time.time() - start_time
                )
            
            # Esegue lo scraping
            html_content = self.scraper.scrape_url(url)
            
            if not html_content:
                return CrawlResult(
                    source_id=source_id,
                    success=False,
                    error="Impossibile scaricare il contenuto",
                    processing_time=time.time() - start_time
                )
            
            # Pulisce il contenuto
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Rimuove elementi non necessari
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
                element.decompose()
            
            # Estrae testo pulito
            text = soup.get_text()
            cleaned_text = clean_text(text)
            
            if len(cleaned_text) < 100:  # Testo troppo corto, probabilmente non utile
                return CrawlResult(
                    source_id=source_id,
                    success=False,
                    error="Contenuto troppo breve o vuoto",
                    processing_time=time.time() - start_time
                )
            
            # Salva nel database
            if self.save_content_to_db(source_id, cleaned_text):
                self.stats['total_content_length'] += len(cleaned_text)
                return CrawlResult(
                    source_id=source_id,
                    success=True,
                    content_length=len(cleaned_text),
                    processing_time=time.time() - start_time
                )
            else:
                return CrawlResult(
                    source_id=source_id,
                    success=False,
                    error="Errore nel salvataggio nel database",
                    processing_time=time.time() - start_time
                )
                
        except Exception as e:
            logger.error(f"Errore nello scraping della fonte {source_id}: {e}")
            return CrawlResult(
                source_id=source_id,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    @retry_on_failure(max_attempts=3, delay=1.0)
    def save_content_to_db(self, source_id: int, content: str) -> bool:
        """Salva il contenuto nel database"""
        try:
            update_data = {"content": content}
            result = self.api.put(f"/sources/{source_id}", json=update_data)
            return result is not None
        except Exception as e:
            logger.error(f"Errore salvataggio fonte {source_id}: {e}")
            return False
    
    def crawl_sources_parallel(self, sources: List[Dict]) -> List[CrawlResult]:
        """Crawl di fonti in parallelo con gestione intelligente della concorrenza"""
        results = []
        
        # Filtra le fonti che devono essere processate
        sources_to_process = [s for s in sources if not self.should_skip_source(s)]
        total_to_process = len(sources_to_process)
        
        logger.info(f"Fonti da processare: {total_to_process} su {len(sources)} totali")
        
        if total_to_process == 0:
            logger.info("Nessuna fonte da processare")
            return []
        
        # Usa progress tracker
        with progress_tracker(total_to_process, "Crawling fonti") as tracker:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Sottometti tutti i job
                future_to_source = {
                    executor.submit(self.scrape_single_source, source): source 
                    for source in sources_to_process
                }
                
                # Processa i risultati man mano che arrivano
                for future in as_completed(future_to_source):
                    source = future_to_source[future]
                    
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Aggiorna statistiche
                        self.stats['processed'] += 1
                        if result.success:
                            self.stats['successful'] += 1
                        else:
                            self.stats['failed'] += 1
                            logger.warning(f"Fallimento fonte {result.source_id}: {result.error}")
                        
                        # Aggiorna progress
                        tracker.update()
                        
                        # Log periodico
                        if self.stats['processed'] % 10 == 0:
                            self._log_progress_stats()
                    
                    except Exception as e:
                        logger.error(f"Errore nel future per fonte {source['id']}: {e}")
                        self.stats['failed'] += 1
                        tracker.update()
        
        return results
    
    def crawl_sources_sequential(self, sources: List[Dict]) -> List[CrawlResult]:
        """Crawl sequenziale per debugging o connessioni instabili"""
        results = []
        sources_to_process = [s for s in sources if not self.should_skip_source(s)]
        
        with progress_tracker(len(sources_to_process), "Crawling sequenziale") as tracker:
            for source in sources_to_process:
                result = self.scrape_single_source(source)
                results.append(result)
                
                # Aggiorna statistiche
                self.stats['processed'] += 1
                if result.success:
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1
                    logger.warning(f"Fallimento fonte {result.source_id}: {result.error}")
                
                tracker.update()
                
                # Pausa tra richieste per essere gentili
                time.sleep(config.scraping.rate_limit_delay)
        
        return results
    
    def _log_progress_stats(self):
        """Log delle statistiche di progresso"""
        success_rate = (self.stats['successful'] / max(self.stats['processed'], 1)) * 100
        avg_content = self.stats['total_content_length'] / max(self.stats['successful'], 1)
        
        logger.info(
            f"Progresso: {self.stats['processed']} processate, "
            f"{self.stats['successful']} successi, "
            f"{self.stats['failed']} fallimenti, "
            f"{self.stats['skipped']} saltate "
            f"(Success rate: {success_rate:.1f}%, "
            f"Contenuto medio: {avg_content:.0f} caratteri)"
        )
    
    def crawl_project(self, project_id: int, parallel: bool = True) -> bool:
        """Crawl completo di un progetto"""
        logger.info(f"=== Inizio crawling progetto {project_id} ===")
        
        # Reset statistiche
        self.stats = {key: 0 for key in self.stats}
        
        try:
            # Recupera le fonti
            sources = self.get_sources_for_project(project_id)
            if not sources:
                logger.warning("Nessuna fonte da processare")
                return True
            
            # Esegue il crawling
            if parallel and len(sources) > 5:  # Parallelo solo se ci sono abbastanza fonti
                logger.info(f"Crawling parallelo con {self.max_workers} worker")
                results = self.crawl_sources_parallel(sources)
            else:
                logger.info("Crawling sequenziale")
                results = self.crawl_sources_sequential(sources)
            
            # Report finale
            self._log_final_stats()
            
            return True
            
        except Exception as e:
            logger.error(f"Errore nel crawling del progetto {project_id}: {e}")
            return False
    
    def _log_final_stats(self):
        """Log delle statistiche finali"""
        total_processed = self.stats['processed']
        success_rate = (self.stats['successful'] / max(total_processed, 1)) * 100
        total_mb = self.stats['total_content_length'] / (1024 * 1024)
        
        logger.info("=== STATISTICHE FINALI CRAWLING ===")
        logger.info(f"Fonti processate: {self.stats['processed']}")
        logger.info(f"Successi: {self.stats['successful']}")
        logger.info(f"Fallimenti: {self.stats['failed']}")
        logger.info(f"Saltate: {self.stats['skipped']}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        logger.info(f"Contenuto totale scaricato: {total_mb:.2f} MB")
        logger.info("===================================")

def main():
    """Funzione principale"""
    # Verifica connessione API
    if not api_client.check_health():
        logger.error("API non raggiungibile. Assicurati che il server sia in esecuzione.")
        sys.exit(1)
    
    # Crea il crawler
    crawler = AdvancedCrawler(max_workers=config.scraping.retry_attempts)
    
    # Mostra progetti disponibili
    projects = crawler.get_all_projects()
    if not projects:
        sys.exit(1)
    
    print("\n=== PROGETTI DISPONIBILI ===")
    for proj in projects:
        print(f"  ID: {proj['id']:<3} | Nome: {proj['name']}")
    
    # Selezione progetto
    try:
        project_choice = input("\nInserisci ID progetto (o 'all' per tutti): ").strip()
        
        if project_choice.lower() == 'all':
            # Crawl di tutti i progetti
            for project in projects:
                logger.info(f"\n=== PROGETTO: {project['name']} ===")
                success = crawler.crawl_project(project['id'])
                if not success:
                    logger.error(f"Errore nel crawling del progetto {project['id']}")
        else:
            project_id = int(project_choice)
            
            # Opzione per crawling parallelo
            parallel_choice = input("Crawling parallelo? (s/n, default=s): ").strip().lower()
            parallel = parallel_choice != 'n'
            
            # Esegue il crawling
            success = crawler.crawl_project(project_id, parallel=parallel)
            
            if success:
                logger.info("Crawling completato con successo")
            else:
                logger.error("Crawling completato con errori")
                sys.exit(1)
    
    except ValueError:
        logger.error("ID progetto non valido")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Crawling interrotto dall'utente")
        sys.exit(0)

if __name__ == "__main__":
    main()
