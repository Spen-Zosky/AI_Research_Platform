# system_manager.py
import sys
import logging
import time
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from utils import api_client, progress_tracker, retry_on_failure
from config import config

logger = logging.getLogger(__name__)

@dataclass
class SystemStats:
    """Statistiche del sistema"""
    timestamp: str
    total_projects: int = 0
    total_sources: int = 0
    sources_with_content: int = 0
    sources_without_content: int = 0
    average_content_length: float = 0.0
    total_content_size_mb: float = 0.0
    last_crawl_stats: Optional[Dict] = None

@dataclass
class HealthCheck:
    """Risultato di un health check"""
    component: str
    status: str  # 'healthy', 'warning', 'error'
    message: str
    details: Optional[Dict] = None

class SystemManager:
    """Gestore completo del sistema con funzionalità di manutenzione"""
    
    def __init__(self):
        self.api = api_client
        self.stats_file = Path("logs/system_stats.json")
        self.ensure_logs_directory()
    
    def ensure_logs_directory(self):
        """Assicura che la directory logs esista"""
        self.stats_file.parent.mkdir(exist_ok=True)
    
    @retry_on_failure(max_attempts=3, delay=2.0)
    def get_system_stats(self) -> SystemStats:
        """Raccoglie statistiche complete del sistema"""
        logger.info("Raccolta statistiche sistema...")
        
        stats = SystemStats(timestamp=datetime.now().isoformat())
        
        try:
            # Statistiche progetti
            projects = self.api.get("/projects/", params={"limit": 5000})
            if projects:
                stats.total_projects = len(projects)
                
                # Statistiche fonti dettagliate
                total_content_length = 0
                sources_count = 0
                
                for project in projects:
                    project_sources = project.get('sources', [])
                    sources_count += len(project_sources)
                    
                    for source in project_sources:
                        content = source.get('content', '')
                        if content and content.strip():
                            stats.sources_with_content += 1
                            total_content_length += len(content)
                        else:
                            stats.sources_without_content += 1
                
                stats.total_sources = sources_count
                
                if stats.sources_with_content > 0:
                    stats.average_content_length = total_content_length / stats.sources_with_content
                    stats.total_content_size_mb = total_content_length / (1024 * 1024)
            
        except Exception as e:
            logger.error(f"Errore nella raccolta statistiche: {e}")
        
        return stats
    
    def save_stats(self, stats: SystemStats):
        """Salva le statistiche su file"""
        try:
            # Carica statistiche esistenti
            historical_stats = []
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    historical_stats = json.load(f)
            
            # Aggiungi nuove statistiche
            historical_stats.append(asdict(stats))
            
            # Mantieni solo gli ultimi 30 giorni
            cutoff_date = datetime.now() - timedelta(days=30)
            historical_stats = [
                s for s in historical_stats 
                if datetime.fromisoformat(s['timestamp']) > cutoff_date
            ]
            
            # Salva
            with open(self.stats_file, 'w') as f:
                json.dump(historical_stats, f, indent=2)
            
            logger.info(f"Statistiche salvate: {len(historical_stats)} record storici")
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio statistiche: {e}")
    
    def perform_health_checks(self) -> List[HealthCheck]:
        """Esegue controlli di salute del sistema"""
        logger.info("Esecuzione health checks...")
        checks = []
        
        # Check API
        checks.append(self._check_api_health())
        
        # Check Database
        checks.append(self._check_database_health())
        
        # Check Storage
        checks.append(self._check_storage_health())
        
        # Check Content Quality
        checks.append(self._check_content_quality())
        
        return checks
    
    def _check_api_health(self) -> HealthCheck:
        """Controlla la salute dell'API"""
        try:
            start_time = time.time()
            healthy = self.api.check_health()
            response_time = time.time() - start_time
            
            if healthy:
                if response_time < 1.0:
                    return HealthCheck(
                        "API", "healthy", 
                        f"API risponde correttamente ({response_time:.2f}s)",
                        {"response_time": response_time}
                    )
                else:
                    return HealthCheck(
                        "API", "warning", 
                        f"API lenta ({response_time:.2f}s)",
                        {"response_time": response_time}
                    )
            else:
                return HealthCheck("API", "error", "API non raggiungibile")
                
        except Exception as e:
            return HealthCheck("API", "error", f"Errore controllo API: {e}")
    
    def _check_database_health(self) -> HealthCheck:
        """Controlla la salute del database"""
        try:
            projects = self.api.get("/projects/", params={"limit": 1})
            
            if projects is not None:
                return HealthCheck(
                    "Database", "healthy", 
                    "Database accessibile e responsive"
                )
            else:
                return HealthCheck(
                    "Database", "error", 
                    "Database non accessibile"
                )
                
        except Exception as e:
            return HealthCheck("Database", "error", f"Errore database: {e}")
    
    def _check_storage_health(self) -> HealthCheck:
        """Controlla lo stato dello storage"""
        try:
            # Controlla spazio disco
            current_dir = Path.cwd()
            stat = os.statvfs(current_dir)
            
            # Calcola spazio libero in GB
            free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            total_space_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
            usage_percent = ((total_space_gb - free_space_gb) / total_space_gb) * 100
            
            details = {
                "free_space_gb": round(free_space_gb, 2),
                "total_space_gb": round(total_space_gb, 2),
                "usage_percent": round(usage_percent, 1)
            }
            
            if usage_percent > 90:
                return HealthCheck(
                    "Storage", "error", 
                    f"Spazio disco critico ({usage_percent:.1f}% utilizzato)",
                    details
                )
            elif usage_percent > 80:
                return HealthCheck(
                    "Storage", "warning", 
                    f"Spazio disco in esaurimento ({usage_percent:.1f}% utilizzato)",
                    details
                )
            else:
                return HealthCheck(
                    "Storage", "healthy", 
                    f"Spazio disco OK ({free_space_gb:.1f}GB liberi)",
                    details
                )
                
        except Exception as e:
            return HealthCheck("Storage", "error", f"Errore controllo storage: {e}")
    
    def _check_content_quality(self) -> HealthCheck:
        """Controlla la qualità del contenuto"""
        try:
            stats = self.get_system_stats()
            
            if stats.total_sources == 0:
                return HealthCheck(
                    "Content Quality", "warning", 
                    "Nessuna fonte presente nel sistema"
                )
            
            content_ratio = stats.sources_with_content / stats.total_sources
            avg_length = stats.average_content_length
            
            details = {
                "content_ratio": round(content_ratio, 3),
                "average_length": round(avg_length, 0),
                "total_size_mb": round(stats.total_content_size_mb, 2)
            }
            
            if content_ratio < 0.3:
                return HealthCheck(
                    "Content Quality", "warning", 
                    f"Poche fonti con contenuto ({content_ratio:.1%})",
                    details
                )
            elif avg_length < 500:
                return HealthCheck(
                    "Content Quality", "warning", 
                    f"Contenuto medio troppo breve ({avg_length:.0f} caratteri)",
                    details
                )
            else:
                return HealthCheck(
                    "Content Quality", "healthy", 
                    f"Qualità contenuto buona ({content_ratio:.1%} con contenuto)",
                    details
                )
                
        except Exception as e:
            return HealthCheck("Content Quality", "error", f"Errore controllo qualità: {e}")
    
    def cleanup_failed_sources(self) -> int:
        """Rimuove le fonti che non hanno mai avuto successo nel crawling"""
        logger.info("Pulizia fonti fallite...")
        
        cleaned_count = 0
        try:
            projects = self.api.get("/projects/", params={"limit": 5000})
            if not projects:
                return 0
            
            for project in projects:
                sources_to_remove = []
                
                for source in project.get('sources', []):
                    # Criteri per rimozione:
                    # 1. Nessun contenuto
                    # 2. URL non valida
                    # 3. Errori ricorrenti (se implementato tracking errori)
                    
                    content = source.get('content', '')
                    url = source.get('url', '')
                    
                    should_remove = False
                    
                    # URL chiaramente non valide
                    if not url or url.lower() in ['n/a', 'na', 'null', 'none', '']:
                        should_remove = True
                    
                    # URL con pattern problematici
                    problematic_patterns = [
                        'javascript:', 'mailto:', 'tel:', '#',
                        'localhost', '127.0.0.1', '0.0.0.0'
                    ]
                    
                    if any(pattern in url.lower() for pattern in problematic_patterns):
                        should_remove = True
                    
                    if should_remove:
                        sources_to_remove.append(source['id'])
                
                # Rimuovi le fonti problematiche
                for source_id in sources_to_remove:
                    try:
                        result = self.api.delete(f"/sources/{source_id}")
                        if result is not None:
                            cleaned_count += 1
                            logger.debug(f"Rimossa fonte problematica: {source_id}")
                    except Exception as e:
                        logger.warning(f"Errore nella rimozione fonte {source_id}: {e}")
            
            logger.info(f"Pulizia completata: {cleaned_count} fonti rimosse")
            
        except Exception as e:
            logger.error(f"Errore nella pulizia: {e}")
        
        return cleaned_count
    
    def optimize_database(self) -> bool:
        """Ottimizza il database (se PostgreSQL)"""
        logger.info("Ottimizzazione database...")
        
        if 'postgresql' not in config.database.url.lower():
            logger.info("Ottimizzazione disponibile solo per PostgreSQL")
            return True
        
        try:
            from improved_create_tables import DatabaseManager
            db_manager = DatabaseManager()
            db_manager._apply_postgresql_optimizations()
            
            logger.info("Ottimizzazione database completata")
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'ottimizzazione database: {e}")
            return False
    
    def generate_system_report(self) -> str:
        """Genera un report completo del sistema"""
        logger.info("Generazione report sistema...")
        
        # Raccoglie dati
        stats = self.get_system_stats()
        health_checks = self.perform_health_checks()
        
        # Genera report
        report_lines = [
            "=" * 60,
            f"REPORT SISTEMA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            "📊 STATISTICHE GENERALI:",
            f"  Progetti totali: {stats.total_projects}",
            f"  Fonti totali: {stats.total_sources}",
            f"  Fonti con contenuto: {stats.sources_with_content}",
            f"  Fonti senza contenuto: {stats.sources_without_content}",
            f"  Dimensione media contenuto: {stats.average_content_length:.0f} caratteri",
            f"  Dimensione totale: {stats.total_content_size_mb:.2f} MB",
            "",
            "🏥 HEALTH CHECKS:",
        ]
        
        for check in health_checks:
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'error': '❌'
            }.get(check.status, '❓')
            
            report_lines.append(f"  {status_emoji} {check.component}: {check.message}")
            
            if check.details:
                for key, value in check.details.items():
                    report_lines.append(f"    - {key}: {value}")
        
        # Aggiungi raccomandazioni
        report_lines.extend([
            "",
            "💡 RACCOMANDAZIONI:",
        ])
        
        # Raccomandazioni basate sui check
        error_checks = [c for c in health_checks if c.status == 'error']
        warning_checks = [c for c in health_checks if c.status == 'warning']
        
        if error_checks:
            report_lines.append("  🚨 AZIONI URGENTI:")
            for check in error_checks:
                report_lines.append(f"    - Risolvi problema: {check.component}")
        
        if warning_checks:
            report_lines.append("  ⚡ AZIONI CONSIGLIATE:")
            for check in warning_checks:
                report_lines.append(f"    - Monitora: {check.component}")
        
        # Consigli generali
        if stats.sources_without_content > stats.sources_with_content:
            report_lines.append("    - Esegui crawling per popolare il contenuto")
        
        if stats.total_sources > 1000 and stats.average_content_length < 1000:
            report_lines.append("    - Verifica qualità delle fonti")
        
        report_lines.extend([
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def run_maintenance(self) -> bool:
        """Esegue manutenzione completa del sistema"""
        logger.info("=== INIZIO MANUTENZIONE SISTEMA ===")
        
        success = True
        
        try:
            # 1. Raccolta statistiche
            logger.info("1. Raccolta statistiche...")
            stats = self.get_system_stats()
            self.save_stats(stats)
            
            # 2. Health checks
            logger.info("2. Controlli di salute...")
            health_checks = self.perform_health_checks()
            
            # 3. Pulizia
            logger.info("3. Pulizia fonti problematiche...")
            cleaned = self.cleanup_failed_sources()
            
            # 4. Ottimizzazione database
            logger.info("4. Ottimizzazione database...")
            self.optimize_database()
            
            # 5. Report finale
            logger.info("5. Generazione report...")
            report = self.generate_system_report()
            
            # Salva report
            report_file = Path(f"logs/system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(report)
            print(f"\nReport salvato in: {report_file}")
            
            logger.info("=== MANUTENZIONE COMPLETATA ===")
            
        except Exception as e:
            logger.error(f"Errore durante la manutenzione: {e}")
            success = False
        
        return success

class InteractiveSystemManager:
    """Interfaccia interattiva per la gestione del sistema"""
    
    def __init__(self):
        self.manager = SystemManager()
    
    def show_menu(self):
        """Mostra il menu principale"""
        print("\n" + "=" * 50)
        print("🔧 GESTORE SISTEMA - MENU PRINCIPALE")
        print("=" * 50)
        print("1. 📊 Visualizza statistiche sistema")
        print("2. 🏥 Esegui health check")
        print("3. 🧹 Pulizia fonti problematiche")
        print("4. ⚡ Ottimizza database")
        print("5. 📄 Genera report completo")
        print("6. 🔄 Manutenzione completa")
        print("7. 📈 Visualizza trend storici")
        print("8. ❌ Esci")
        print("=" * 50)
    
    def handle_choice(self, choice: str) -> bool:
        """Gestisce la scelta dell'utente"""
        try:
            if choice == '1':
                self._show_stats()
            elif choice == '2':
                self._run_health_checks()
            elif choice == '3':
                self._cleanup_sources()
            elif choice == '4':
                self._optimize_database()
            elif choice == '5':
                self._generate_report()
            elif choice == '6':
                self._run_full_maintenance()
            elif choice == '7':
                self._show_historical_trends()
            elif choice == '8':
                return False
            else:
                print("Scelta non valida.")
            
            input("\nPremi INVIO per continuare...")
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'esecuzione comando: {e}")
            print(f"Errore: {e}")
            input("\nPremi INVIO per continuare...")
            return True
    
    def _show_stats(self):
        """Mostra statistiche del sistema"""
        print("\n📊 RACCOLTA STATISTICHE...")
        stats = self.manager.get_system_stats()
        
        print(f"""
📈 STATISTICHE SISTEMA:
  Timestamp: {stats.timestamp}
  Progetti: {stats.total_projects}
  Fonti totali: {stats.total_sources}
  Fonti con contenuto: {stats.sources_with_content}
  Fonti senza contenuto: {stats.sources_without_content}
  Contenuto medio: {stats.average_content_length:.0f} caratteri
  Dimensione totale: {stats.total_content_size_mb:.2f} MB
        """)
    
    def _run_health_checks(self):
        """Esegue health checks"""
        print("\n🏥 ESECUZIONE HEALTH CHECKS...")
        checks = self.manager.perform_health_checks()
        
        for check in checks:
            status_emoji = {'healthy': '✅', 'warning': '⚠️', 'error': '❌'}.get(check.status, '❓')
            print(f"  {status_emoji} {check.component}: {check.message}")
    
    def _cleanup_sources(self):
        """Pulizia fonti problematiche"""
        print("\n🧹 PULIZIA FONTI PROBLEMATICHE...")
        confirm = input("Continuare con la pulizia? (s/n): ").lower()
        
        if confirm in ['s', 'si', 'y', 'yes']:
            cleaned = self.manager.cleanup_failed_sources()
            print(f"✅ Rimosse {cleaned} fonti problematiche")
        else:
            print("Pulizia annullata.")
    
    def _optimize_database(self):
        """Ottimizzazione database"""
        print("\n⚡ OTTIMIZZAZIONE DATABASE...")
        success = self.manager.optimize_database()
        if success:
            print("✅ Ottimizzazione completata")
        else:
            print("❌ Errore nell'ottimizzazione")
    
    def _generate_report(self):
        """Genera report"""
        print("\n📄 GENERAZIONE REPORT...")
        report = self.manager.generate_system_report()
        print(report)
    
    def _run_full_maintenance(self):
        """Manutenzione completa"""
        print("\n🔄 MANUTENZIONE COMPLETA...")
        confirm = input("Eseguire manutenzione completa del sistema? (s/n): ").lower()
        
        if confirm in ['s', 'si', 'y', 'yes']:
            success = self.manager.run_maintenance()
            if success:
                print("✅ Manutenzione completata con successo")
            else:
                print("❌ Manutenzione completata con errori")
        else:
            print("Manutenzione annullata.")
    
    def _show_historical_trends(self):
        """Mostra trend storici"""
        print("\n📈 TREND STORICI...")
        
        try:
            if self.manager.stats_file.exists():
                with open(self.manager.stats_file, 'r') as f:
                    historical_stats = json.load(f)
                
                if len(historical_stats) >= 2:
                    latest = historical_stats[-1]
                    previous = historical_stats[-2]
                    
                    print(f"Confronto con rilevazione precedente:")
                    print(f"  Progetti: {latest['total_projects']} ({latest['total_projects'] - previous['total_projects']:+d})")
                    print(f"  Fonti: {latest['total_sources']} ({latest['total_sources'] - previous['total_sources']:+d})")
                    print(f"  Contenuti: {latest['sources_with_content']} ({latest['sources_with_content'] - previous['sources_with_content']:+d})")
                else:
                    print("Dati storici insufficienti per il confronto")
            else:
                print("Nessun dato storico disponibile")
                
        except Exception as e:
            print(f"Errore nella lettura dati storici: {e}")
    
    def run(self):
        """Esegue l'interfaccia interattiva"""
        print("🔧 GESTORE SISTEMA AVVIATO")
        
        # Verifica connessione
        if not self.manager.api.check_health():
            print("❌ API non raggiungibile. Verifica che il server sia attivo.")
            return
        
        while True:
            self.show_menu()
            choice = input("\nScegli un'opzione (1-8): ").strip()
            
            if not self.handle_choice(choice):
                break
        
        print("👋 Gestore sistema terminato.")

def main():
    """Funzione principale"""
    try:
        if len(sys.argv) == 1:
            # Modalità interattiva
            interactive_manager = InteractiveSystemManager()
            interactive_manager.run()
        
        elif len(sys.argv) == 2:
            # Modalità da riga di comando
            command = sys.argv[1].lower()
            manager = SystemManager()
            
            if command == 'stats':
                stats = manager.get_system_stats()
                manager.save_stats(stats)
                print("Statistiche raccolte e salvate")
            
            elif command == 'health':
                checks = manager.perform_health_checks()
                for check in checks:
                    status = {'healthy': '✅', 'warning': '⚠️', 'error': '❌'}.get(check.status, '❓')
                    print(f"{status} {check.component}: {check.message}")
            
            elif command == 'cleanup':
                cleaned = manager.cleanup_failed_sources()
                print(f"Rimosse {cleaned} fonti problematiche")
            
            elif command == 'optimize':
                success = manager.optimize_database()
                print("Ottimizzazione completata" if success else "Errore nell'ottimizzazione")
            
            elif command == 'report':
                report = manager.generate_system_report()
                print(report)
            
            elif command == 'maintenance':
                success = manager.run_maintenance()
                sys.exit(0 if success else 1)
            
            else:
                print("Comandi disponibili:")
                print("  stats       - Raccoglie statistiche")
                print("  health      - Esegue health check")
                print("  cleanup     - Pulizia fonti problematiche")
                print("  optimize    - Ottimizza database")
                print("  report      - Genera report completo")
                print("  maintenance - Manutenzione completa")
        
        else:
            print("Utilizzo:")
            print("  python system_manager.py              # Modalità interattiva")
            print("  python system_manager.py [comando]    # Comando specifico")
    
    except KeyboardInterrupt:
        logger.info("Gestore sistema interrotto dall'utente")
    except Exception as e:
        logger.error(f"Errore inaspettato: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()