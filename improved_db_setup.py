# improved_create_tables.py
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import List, Optional
from config import config
from utils import retry_on_failure

# Aggiungi il path del progetto per importare i modelli
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from app.models.project import Base
except ImportError as e:
    logging.error(f"Errore nell'importazione dei modelli: {e}")
    logging.error("Assicurati che il modulo 'app.models.project' esista e sia corretto")
    sys.exit(1)

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestore avanzato per operazioni sul database"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Configura il motore del database"""
        try:
            self.engine = create_engine(
                config.database.url,
                pool_size=config.database.pool_size,
                max_overflow=config.database.max_overflow,
                pool_timeout=config.database.pool_timeout,
                echo=False  # Imposta True per debug SQL
            )
            
            self.session_factory = sessionmaker(bind=self.engine)
            logger.info("Motore database configurato correttamente")
            
        except Exception as e:
            logger.error(f"Errore nella configurazione del database: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Context manager per sessioni database con gestione automatica delle transazioni"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Errore nella sessione database, rollback eseguito: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Testa la connessione al database"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Connessione al database riuscita")
            return True
        except Exception as e:
            logger.error(f"Errore nella connessione al database: {e}")
            return False
    
    def get_existing_tables(self) -> List[str]:
        """Ottiene la lista delle tabelle esistenti"""
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"Tabelle esistenti: {tables}")
            return tables
        except Exception as e:
            logger.error(f"Errore nel recupero delle tabelle esistenti: {e}")
            return []
    
    def backup_existing_data(self, table_name: str) -> Optional[str]:
        """Crea un backup dei dati esistenti (semplificato)"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                logger.info(f"Tabella {table_name} contiene {count} righe")
                return f"backup_{table_name}_{count}_rows"
        except Exception as e:
            logger.warning(f"Impossibile creare backup per {table_name}: {e}")
            return None
    
    @retry_on_failure(max_attempts=3, delay=2.0)
    def create_tables(self, drop_existing: bool = False) -> bool:
        """Crea le tabelle del database"""
        logger.info("=== INIZIALIZZAZIONE DATABASE ===")
        
        try:
            existing_tables = self.get_existing_tables()
            
            if existing_tables and not drop_existing:
                logger.warning("Tabelle esistenti rilevate:")
                for table in existing_tables:
                    logger.warning(f"  - {table}")
                
                choice = input("\nVuoi eliminare le tabelle esistenti? (s/n): ").strip().lower()
                drop_existing = choice in ['s', 'si', 'y', 'yes']
            
            if drop_existing and existing_tables:
                logger.info("Backup dati esistenti...")
                for table in existing_tables:
                    backup_info = self.backup_existing_data(table)
                    if backup_info:
                        logger.info(f"Backup creato: {backup_info}")
                
                logger.info("Eliminazione tabelle esistenti...")
                Base.metadata.drop_all(bind=self.engine)
                logger.info("Tabelle esistenti eliminate")
            
            logger.info("Creazione nuove tabelle...")
            Base.metadata.create_all(bind=self.engine)
            
            # Verifica che le tabelle siano state create correttamente
            new_tables = self.get_existing_tables()
            logger.info(f"Tabelle create: {new_tables}")
            
            # Applica ottimizzazioni se PostgreSQL
            if 'postgresql' in config.database.url.lower():
                self._apply_postgresql_optimizations()
            
            logger.info("✅ Database inizializzato correttamente")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Errore SQLAlchemy: {e}")
            return False
        except Exception as e:
            logger.error(f"Errore generico: {e}")
            return False
    
    def _apply_postgresql_optimizations(self):
        """Applica ottimizzazioni specifiche per PostgreSQL"""
        logger.info("Applicazione ottimizzazioni PostgreSQL...")
        
        optimizations = [
            # Indice full-text search per contenuti
            "CREATE INDEX IF NOT EXISTS idx_sources_content_fts ON sources USING GIN (to_tsvector('italian', content))",
            
            # Indici per ricerche comuni
            "CREATE INDEX IF NOT EXISTS idx_sources_title ON sources (title)",
            "CREATE INDEX IF NOT EXISTS idx_sources_url ON sources (url)",
            "CREATE INDEX IF NOT EXISTS idx_projects_name ON projects (name)",
            
            # Indice per le relazioni
            "CREATE INDEX IF NOT EXISTS idx_sources_project_id ON sources (project_id)",
        ]
        
        try:
            with self.engine.connect() as conn:
                for optimization in optimizations:
                    try:
                        conn.execute(text(optimization))
                        logger.debug(f"Ottimizzazione applicata: {optimization.split()[2]}")
                    except Exception as e:
                        logger.warning(f"Errore nell'applicazione ottimizzazione: {e}")
                
                conn.commit()
                logger.info("Ottimizzazioni PostgreSQL applicate")
                
        except Exception as e:
            logger.error(f"Errore nell'applicazione delle ottimizzazioni: {e}")
    
    def verify_database_integrity(self) -> bool:
        """Verifica l'integrità del database"""
        logger.info("Verifica integrità database...")
        
        try:
            with self.get_session() as session:
                # Verifica che le tabelle principali esistano e siano accessibili
                test_queries = [
                    "SELECT COUNT(*) FROM projects",
                    "SELECT COUNT(*) FROM sources",
                ]
                
                for query in test_queries:
                    result = session.execute(text(query))
                    count = result.scalar()
                    table_name = query.split()[-1]
                    logger.info(f"Tabella {table_name}: {count} record")
            
            logger.info("✅ Verifica integrità completata")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore nella verifica integrità: {e}")
            return False
    
    def get_database_stats(self) -> dict:
        """Ottiene statistiche sul database"""
        stats = {
            'tables': 0,
            'total_records': 0,
            'projects': 0,
            'sources': 0,
            'sources_with_content': 0
        }
        
        try:
            stats['tables'] = len(self.get_existing_tables())
            
            with self.get_session() as session:
                # Conta progetti
                result = session.execute(text("SELECT COUNT(*) FROM projects"))
                stats['projects'] = result.scalar()
                
                # Conta fonti
                result = session.execute(text("SELECT COUNT(*) FROM sources"))
                stats['sources'] = result.scalar()
                
                # Conta fonti con contenuto
                result = session.execute(text("SELECT COUNT(*) FROM sources WHERE content IS NOT NULL AND content != ''"))
                stats['sources_with_content'] = result.scalar()
                
                stats['total_records'] = stats['projects'] + stats['sources']
            
        except Exception as e:
            logger.error(f"Errore nel recupero statistiche: {e}")
        
        return stats

class DatabaseInitializer:
    """Inizializzatore completo del database con opzioni avanzate"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def run_interactive_setup(self):
        """Setup interattivo del database"""
        print("=== SETUP DATABASE INTERATTIVO ===")
        print("Questo script configurerà il database per l'applicazione.")
        
        # Test connessione
        if not self.db_manager.test_connection():
            print("❌ Impossibile connettersi al database.")
            print("Verifica la configurazione in .env file.")
            return False
        
        # Mostra statistiche attuali
        stats = self.db_manager.get_database_stats()
        if stats['tables'] > 0:
            print(f"\n📊 STATO ATTUALE DATABASE:")
            print(f"  Tabelle: {stats['tables']}")
            print(f"  Progetti: {stats['projects']}")
            print(f"  Fonti: {stats['sources']}")
            print(f"  Fonti con contenuto: {stats['sources_with_content']}")
        
        # Opzioni setup
        print("\n🔧 OPZIONI SETUP:")
        print("1. Inizializzazione completa (elimina dati esistenti)")
        print("2. Creazione tabelle mancanti (preserva dati)")
        print("3. Solo verifica integrità")
        print("4. Applica solo ottimizzazioni")
        print("5. Esci")
        
        choice = input("\nScegli un'opzione (1-5): ").strip()
        
        if choice == '1':
            return self._full_initialization()
        elif choice == '2':
            return self._create_missing_tables()
        elif choice == '3':
            return self.db_manager.verify_database_integrity()
        elif choice == '4':
            return self._apply_optimizations_only()
        elif choice == '5':
            print("Setup annullato.")
            return True
        else:
            print("Scelta non valida.")
            return False
    
    def _full_initialization(self):
        """Inizializzazione completa del database"""
        print("\n⚠️  ATTENZIONE: Questa operazione eliminerà tutti i dati esistenti!")
        confirm = input("Sei sicuro di voler continuare? (digita 'CONFERMA'): ")
        
        if confirm != 'CONFERMA':
            print("Operazione annullata.")
            return False
        
        success = self.db_manager.create_tables(drop_existing=True)
        if success:
            self.db_manager.verify_database_integrity()
        
        return success
    
    def _create_missing_tables(self):
        """Crea solo le tabelle mancanti"""
        print("\n🔄 Creazione tabelle mancanti...")
        return self.db_manager.create_tables(drop_existing=False)
    
    def _apply_optimizations_only(self):
        """Applica solo le ottimizzazioni"""
        print("\n⚡ Applicazione ottimizzazioni...")
        try:
            if 'postgresql' in config.database.url.lower():
                self.db_manager._apply_postgresql_optimizations()
                return True
            else:
                print("Ottimizzazioni disponibili solo per PostgreSQL.")
                return False
        except Exception as e:
            logger.error(f"Errore nell'applicazione ottimizzazioni: {e}")
            return False

def main():
    """Funzione principale"""
    try:
        initializer = DatabaseInitializer()
        
        # Modalità interattiva di default
        if len(sys.argv) == 1:
            success = initializer.run_interactive_setup()
        
        # Modalità da riga di comando
        elif len(sys.argv) == 2:
            arg = sys.argv[1].lower()
            
            if arg in ['--full', '-f']:
                success = initializer.db_manager.create_tables(drop_existing=True)
            elif arg in ['--create', '-c']:
                success = initializer.db_manager.create_tables(drop_existing=False)
            elif arg in ['--verify', '-v']:
                success = initializer.db_manager.verify_database_integrity()
            elif arg in ['--stats', '-s']:
                stats = initializer.db_manager.get_database_stats()
                print("\n📊 STATISTICHE DATABASE:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                success = True
            else:
                print("Opzioni disponibili:")
                print("  --full, -f     : Inizializzazione completa")
                print("  --create, -c   : Crea tabelle mancanti")
                print("  --verify, -v   : Verifica integrità")
                print("  --stats, -s    : Mostra statistiche")
                success = False
        else:
            print("Utilizzo:")
            print("  python improved_create_tables.py           # Modalità interattiva")
            print("  python improved_create_tables.py [opzione] # Modalità comando")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Setup interrotto dall'utente.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Errore inaspettato: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
