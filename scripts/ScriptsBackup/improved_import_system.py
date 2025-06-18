# improved_import_data.py
import os
import sys
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from utils import api_client, progress_tracker, retry_on_failure, validate_url, safe_str, safe_int
from config import config

logger = logging.getLogger(__name__)

@dataclass
class ImportStats:
    """Statistiche di importazione"""
    total_rows: int = 0
    successful_imports: int = 0
    failed_imports: int = 0
    skipped_rows: int = 0
    duplicate_sources: int = 0
    created_projects: int = 0

@dataclass
class ImportResult:
    """Risultato di una singola importazione"""
    success: bool
    message: str
    project_id: Optional[int] = None
    source_id: Optional[int] = None

class DataImporter:
    """Sistema avanzato di importazione dati da file Excel/CSV"""
    
    def __init__(self):
        self.api = api_client
        self.project_cache: Dict[str, int] = {}
        self.stats = ImportStats()
        
        # Configurazione colonne per diversi formati di file
        self.column_mappings = {
            'standard': {
                'project': ['Contesto', 'Context', 'Progetto', 'Project'],
                'title': ['Nome', 'Name', 'Title', 'Titolo'],
                'url': ['URL', 'Link', 'Collegamento', 'Indirizzo']
            }
        }
    
    def detect_file_format(self, df: pd.DataFrame) -> Optional[Dict[str, str]]:
        """Rileva automaticamente il formato del file e mappa le colonne"""
        columns = [col.strip() for col in df.columns]
        column_mapping = {}
        
        logger.info(f"Colonne rilevate nel file: {columns}")
        
        # Cerca le colonne necessarie
        for field, possible_names in self.column_mappings['standard'].items():
            found_column = None
            for possible_name in possible_names:
                for col in columns:
                    if col.lower() == possible_name.lower():
                        found_column = col
                        break
                if found_column:
                    break
            
            if found_column:
                column_mapping[field] = found_column
                logger.info(f"Campo '{field}' mappato su colonna '{found_column}'")
            else:
                logger.error(f"Campo obbligatorio '{field}' non trovato nelle colonne: {possible_names}")
                return None
        
        return column_mapping
    
    @retry_on_failure(max_attempts=3, delay=1.0)
    def get_or_create_project(self, project_name: str) -> Optional[int]:
        """Ottiene o crea un progetto con cache locale"""
        project_name = safe_str(project_name).strip()
        
        if not project_name:
            logger.warning("Nome progetto vuoto")
            return None
        
        # Controlla cache
        if project_name in self.project_cache:
            return self.project_cache[project_name]
        
        logger.debug(f"Gestione progetto: '{project_name}'")
        
        try:
            # Prima cerca se esiste già
            projects = self.api.get("/projects/", params={"limit": 2000})
            if projects:
                for project in projects:
                    if project['name'].strip().lower() == project_name.lower():
                        project_id = project['id']
                        self.project_cache[project_name] = project_id
                        logger.debug(f"Progetto esistente trovato: {project_name} (ID: {project_id})")
                        return project_id
            
            # Se non esiste, crealo
            project_data = {
                "name": project_name,
                "description": f"Progetto creato automaticamente per il contesto '{project_name}'"
            }
            
            result = self.api.post("/projects/", json=project_data)
            if result:
                project_id = result['id']
                self.project_cache[project_name] = project_id
                self.stats.created_projects += 1
                logger.info(f"Nuovo progetto creato: {project_name} (ID: {project_id})")
                return project_id
            
        except Exception as e:
            logger.error(f"Errore nella gestione del progetto '{project_name}': {e}")
        
        return None
    
    @retry_on_failure(max_attempts=3, delay=1.0)
    def import_source(self, project_id: int, title: str, url: str) -> ImportResult:
        """Importa una singola fonte"""
        try:
            # Valida e normalizza i dati
            title = safe_str(title).strip()
            if not title:
                return ImportResult(False, "Titolo vuoto")
            
            try:
                normalized_url = validate_url(url)
            except ValueError as e:
                return ImportResult(False, f"URL non valida: {e}")
            
            # Prepara i dati
            source_data = {
                "title": title,
                "url": normalized_url
            }
            
            # Importa tramite API
            result = self.api.post(f"/projects/{project_id}/sources/", json=source_data)
            
            if result:
                source_id = result.get('id')
                logger.debug(f"Fonte importata: {title} (ID: {source_id})")
                return ImportResult(True, "Importazione riuscita", project_id, source_id)
            else:
                return ImportResult(False, "Errore API durante l'importazione")
                
        except Exception as e:
            logger.error(f"Errore nell'importazione di '{title}': {e}")
            return ImportResult(False, f"Errore: {e}")
    
    def validate_row_data(self, row: pd.Series, column_mapping: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Valida e estrae i dati da una riga"""
        try:
            project_name = safe_str(row.get(column_mapping['project'], ''))
            title = safe_str(row.get(column_mapping['title'], ''))
            url = safe_str(row.get(column_mapping['url'], ''))
            
            # Controlli di validità
            if not all([project_name, title, url]):
                missing_fields = []
                if not project_name: missing_fields.append('progetto')
                if not title: missing_fields.append('titolo')
                if not url: missing_fields.append('url')
                logger.debug(f"Riga saltata - campi mancanti: {', '.join(missing_fields)}")
                return None
            
            return {
                'project': project_name,
                'title': title,
                'url': url
            }
            
        except Exception as e:
            logger.debug(f"Errore nella validazione della riga: {e}")
            return None
    
    def import_from_dataframe(self, df: pd.DataFrame, file_name: str = "Unknown") -> bool:
        """Importa dati da un DataFrame pandas"""
        logger.info(f"=== Inizio importazione da {file_name} ===")
        
        # Reset statistiche
        self.stats = ImportStats()
        self.stats.total_rows = len(df)
        
        # Rileva formato del file
        column_mapping = self.detect_file_format(df)
        if not column_mapping:
            logger.error("Impossibile rilevare il formato del file")
            return False
        
        logger.info(f"Formato rilevato. Processamento di {self.stats.total_rows} righe...")
        
        # Processa le righe con progress tracking
        with progress_tracker(self.stats.total_rows, f"Importazione {file_name}") as tracker:
            for index, row in df.iterrows():
                # Valida i dati della riga
                row_data = self.validate_row_data(row, column_mapping)
                
                if not row_data:
                    self.stats.skipped_rows += 1
                    tracker.update()
                    continue
                
                # Ottieni/crea il progetto
                project_id = self.get_or_create_project(row_data['project'])
                
                if not project_id:
                    self.stats.failed_imports += 1
                    logger.warning(f"Impossibile gestire progetto: {row_data['project']}")
                    tracker.update()
                    continue
                
                # Importa la fonte
                result = self.import_source(project_id, row_data['title'], row_data['url'])
                
                if result.success:
                    self.stats.successful_imports += 1
                else:
                    self.stats.failed_imports += 1
                    if "duplicate" in result.message.lower() or "already exists" in result.message.lower():
                        self.stats.duplicate_sources += 1
                
                tracker.update()
                
                # Log periodico ogni 50 righe
                if (index + 1) % 50 == 0:
                    self._log_progress()
        
        # Log finale
        self._log_final_stats(file_name)
        
        return self.stats.successful_imports > 0
    
    def import_from_excel(self, file_path: str) -> bool:
        """Importa dati da file Excel"""
        try:
            logger.info(f"Lettura file Excel: {file_path}")
            df = pd.read_excel(file_path)
            return self.import_from_dataframe(df, Path(file_path).name)
            
        except Exception as e:
            logger.error(f"Errore nella lettura del file Excel {file_path}: {e}")
            return False
    
    def import_from_csv(self, file_path: str, **kwargs) -> bool:
        """Importa dati da file CSV"""
        try:
            logger.info(f"Lettura file CSV: {file_path}")
            # Prova diversi encoding
            encodings = ['utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, **kwargs)
                    logger.info(f"File letto con encoding {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                logger.error("Impossibile leggere il file CSV con nessun encoding")
                return False
            
            return self.import_from_dataframe(df, Path(file_path).name)
            
        except Exception as e:
            logger.error(f"Errore nella lettura del file CSV {file_path}: {e}")
            return False
    
    def import_multiple_files(self, file_paths: List[str]) -> bool:
        """Importa da multipli file"""
        logger.info(f"Importazione batch di {len(file_paths)} file")
        
        total_success = True
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File non trovato: {file_path}")
                continue
            
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.xlsx', '.xls']:
                success = self.import_from_excel(file_path)
            elif file_ext == '.csv':
                success = self.import_from_csv(file_path)
            else:
                logger.warning(f"Formato file non supportato: {file_path}")
                continue
            
            if not success:
                total_success = False
                logger.error(f"Errore nell'importazione di {file_path}")
        
        return total_success
    
    def _log_progress(self):
        """Log del progresso durante l'importazione"""
        processed = self.stats.successful_imports + self.stats.failed_imports + self.stats.skipped_rows
        success_rate = (self.stats.successful_imports / max(processed, 1)) * 100
        
        logger.info(
            f"Progresso: {processed}/{self.stats.total_rows} righe processate, "
            f"{self.stats.successful_imports} successi, "
            f"{self.stats.failed_imports} fallimenti, "
            f"{self.stats.skipped_rows} saltate "
            f"(Success rate: {success_rate:.1f}%)"
        )
    
    def _log_final_stats(self, file_name: str):
        """Log delle statistiche finali"""
        success_rate = (self.stats.successful_imports / max(self.stats.total_rows, 1)) * 100
        
        logger.info(f"=== STATISTICHE IMPORTAZIONE {file_name} ===")
        logger.info(f"Righe totali: {self.stats.total_rows}")
        logger.info(f"Importazioni riuscite: {self.stats.successful_imports}")
        logger.info(f"Importazioni fallite: {self.stats.failed_imports}")
        logger.info(f"Righe saltate: {self.stats.skipped_rows}")
        logger.info(f"Fonti duplicate: {self.stats.duplicate_sources}")
        logger.info(f"Progetti creati: {self.stats.created_projects}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        logger.info("=" * 50)

class InteractiveImporter:
    """Interfaccia interattiva per l'importazione"""
    
    def __init__(self):
        self.importer = DataImporter()
    
    def show_available_files(self) -> List[str]:
        """Mostra i file disponibili per l'importazione"""
        current_dir = Path.cwd()
        supported_extensions = ['.xlsx', '.xls', '.csv']
        
        available_files = []
        for ext in supported_extensions:
            files = list(current_dir.glob(f"*{ext}"))
            available_files.extend(files)
        
        if available_files:
            print("\n=== FILE DISPONIBILI PER L'IMPORTAZIONE ===")
            for i, file_path in enumerate(available_files, 1):
                print(f"  {i}: {file_path.name}")
            print(f"  {len(available_files) + 1}: File personalizzato (inserisci percorso)")
            print(f"  {len(available_files) + 2}: Importazione batch (tutti i file)")
        else:
            print("\nNessun file di dati trovato nella directory corrente.")
        
        return available_files
    
    def get_user_choice(self, available_files: List[str]) -> Optional[List[str]]:
        """Ottiene la scelta dell'utente per i file da importare"""
        if not available_files:
            custom_path = input("Inserisci il percorso del file da importare: ").strip()
            if custom_path and os.path.exists(custom_path):
                return [custom_path]
            else:
                print("File non trovato.")
                return None
        
        try:
            choice = input(f"\nScegli un'opzione (1-{len(available_files) + 2}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(available_files):
                # File specifico
                return [str(available_files[choice_num - 1])]
            elif choice_num == len(available_files) + 1:
                # File personalizzato
                custom_path = input("Inserisci il percorso del file: ").strip()
                if custom_path and os.path.exists(custom_path):
                    return [custom_path]
                else:
                    print("File non trovato.")
                    return None
            elif choice_num == len(available_files) + 2:
                # Batch di tutti i file
                return [str(f) for f in available_files]
            else:
                print("Scelta non valida.")
                return None
                
        except ValueError:
            print("Inserisci un numero valido.")
            return None
    
    def confirm_import(self, file_paths: List[str]) -> bool:
        """Chiede conferma prima dell'importazione"""
        print(f"\nFile da importare:")
        for path in file_paths:
            print(f"  - {Path(path).name}")
        
        confirm = input("\nProcedere con l'importazione? (s/n): ").strip().lower()
        return confirm in ['s', 'si', 'y', 'yes']
    
    def run(self):
        """Esegue l'importazione interattiva"""
        logger.info("=== SISTEMA DI IMPORTAZIONE DATI ===")
        
        # Verifica connessione API
        if not self.importer.api.check_health():
            logger.error("API non raggiungibile. Assicurati che il server sia in esecuzione.")
            return False
        
        # Mostra file disponibili
        available_files = self.show_available_files()
        
        # Ottieni scelta utente
        chosen_files = self.get_user_choice(available_files)
        if not chosen_files:
            logger.info("Importazione annullata.")
            return False
        
        # Conferma importazione
        if not self.confirm_import(chosen_files):
            logger.info("Importazione annullata dall'utente.")
            return False
        
        # Esegue l'importazione
        logger.info("Inizio importazione...")
        success = self.importer.import_multiple_files(chosen_files)
        
        if success:
            logger.info("Importazione completata con successo!")
        else:
            logger.error("Importazione completata con errori.")
        
        return success

def main():
    """Funzione principale"""
    try:
        # Modalità interattiva se nessun argomento
        if len(sys.argv) == 1:
            interactive_importer = InteractiveImporter()
            success = interactive_importer.run()
            sys.exit(0 if success else 1)
        
        # Modalità da riga di comando
        elif len(sys.argv) == 2:
            file_path = sys.argv[1]
            
            if not os.path.exists(file_path):
                logger.error(f"File non trovato: {file_path}")
                sys.exit(1)
            
            # Verifica connessione API
            importer = DataImporter()
            if not importer.api.check_health():
                logger.error("API non raggiungibile.")
                sys.exit(1)
            
            # Importa il file
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.xlsx', '.xls']:
                success = importer.import_from_excel(file_path)
            elif file_ext == '.csv':
                success = importer.import_from_csv(file_path)
            else:
                logger.error(f"Formato file non supportato: {file_ext}")
                sys.exit(1)
            
            sys.exit(0 if success else 1)
        
        else:
            print("Utilizzo:")
            print("  python improved_import_data.py                    # Modalità interattiva")
            print("  python improved_import_data.py <file_path>        # Importa file specifico")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Importazione interrotta dall'utente.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Errore inaspettato: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()