#!/usr/bin/env python3
"""
Enhanced AI Research Platform Documentation Generator
Genera documentazione completa usando tutti i comandi di analisi
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class EnhancedPlatformDocumentationGenerator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"platform_docs_{self.timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # File di output
        self.md_file = f"{self.output_dir}/platform_current_config.md"
        self.txt_file = f"{self.output_dir}/platform_current_config.txt"
        self.json_file = f"{self.output_dir}/platform_complete_data.json"
        
    def run_command(self, command, description=""):
        """Esegue comando e restituisce output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
            return output.strip()
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def append_to_files(self, section_title, content):
        """Appende contenuto a entrambi i file"""
        # Formato Markdown
        with open(self.md_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## {section_title}\n\n```\n{content}\n```\n")
        
        # Formato TXT
        with open(self.txt_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n{section_title}\n{'='*60}\n{content}\n")

    def collect_project_structure(self):
        """📁 Struttura del Progetto"""
        print("🔍 Analizzando struttura progetto...")
        
        # Struttura directory principale
        output = self.run_command("ls -la")
        self.append_to_files("STRUTTURA DIRECTORY PRINCIPALE", output)
        
        # Struttura completa fino a 3 livelli
        output = self.run_command("find . -maxdepth 3 -type d | head -20")
        self.append_to_files("STRUTTURA COMPLETA (fino a 3 livelli)", output)
        
        # File Python principali
        output = self.run_command("find . -name '*.py' -type f | head -20")
        self.append_to_files("FILE PYTHON PRINCIPALI", output)
        
        return {"project_structure": "completed"}

    def collect_configuration_setup(self):
        """🔧 Configurazione e Setup"""
        print("⚙️ Raccogliendo configurazioni...")
        
        # File di configurazione
        output = self.run_command('ls -la | grep -E "\\.(env|cfg|ini|toml|yaml|yml|conf)$"')
        self.append_to_files("FILE DI CONFIGURAZIONE", output)
        
        # Contenuto .env (mascherato)
        env_command = '''
if [ -f .env ]; then
    echo "File .env trovato:"
    cat .env | sed 's/password=[^[:space:]]*/password=***HIDDEN***/g'
else
    echo "File .env non trovato"
fi
        '''
        output = self.run_command(env_command)
        self.append_to_files("CONTENUTO .ENV", output)
        
        # Requirements/Dipendenze
        req_command = '''
if [ -f requirements.txt ]; then
    echo "requirements.txt:"
    cat requirements.txt
elif [ -f pyproject.toml ]; then
    echo "pyproject.toml:"
    cat pyproject.toml
else
    echo "Nessun file di dipendenze trovato"
fi
        '''
        output = self.run_command(req_command)
        self.append_to_files("REQUIREMENTS/DIPENDENZE", output)
        
        return {"configuration": "completed"}

    def collect_python_info(self):
        """🐍 Informazioni Python"""
        print("🐍 Raccogliendo info Python...")
        
        # Versione Python
        output = self.run_command("python --version")
        output += "\n" + self.run_command("python3 --version 2>/dev/null || echo 'python3 non trovato'")
        self.append_to_files("VERSIONE PYTHON", output)
        
        # Moduli installati
        output = self.run_command('pip list | grep -E "(fastapi|flask|django|sqlalchemy|requests|pandas)" || echo "Nessun modulo web framework trovato"')
        self.append_to_files("MODULI INSTALLATI (sample)", output)
        
        # Virtual Environment
        venv_info = f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'Not set')}\n"
        venv_info += self.run_command("which python")
        self.append_to_files("VIRTUAL ENVIRONMENT", venv_info)
        
        # Lista completa pip
        output = self.run_command("pip list --format=freeze")
        self.append_to_files("PIP LIST COMPLETA", output)
        
        return {"python_info": "completed"}

    def collect_database_info(self):
        """🗄️ Database e Modelli"""
        print("🗄️ Analizzando database...")
        
        # File modelli/database
        output = self.run_command('find . -name "*model*" -o -name "*schema*" -o -name "*database*" | grep "\\.py$" | head -20')
        self.append_to_files("FILE MODELLI/DATABASE", output)
        
        # File configurazione DB
        db_files = self.run_command('find . -name "*.db" -o -name "*.sqlite*"')
        db_processes = self.run_command('ps aux | grep -E "(postgres|mysql|sqlite)" | grep -v grep || echo "Nessun processo database trovato"')
        self.append_to_files("FILE CONFIGURAZIONE DB", db_files)
        self.append_to_files("PROCESSI DATABASE", db_processes)
        
        # Contenuto modelli principali
        for model_file in ["app/models/project.py", "app/models/source.py", "app/models/entity.py"]:
            if os.path.exists(model_file):
                content = self.run_command(f"cat {model_file}")
                self.append_to_files(f"CONTENUTO {model_file}", content)
        
        # Schema database
        for schema_file in ["app/schemas/project.py", "app/schemas/source.py", "app/schemas/entity.py"]:
            if os.path.exists(schema_file):
                content = self.run_command(f"cat {schema_file}")
                self.append_to_files(f"CONTENUTO {schema_file}", content)
        
        return {"database_info": "completed"}

    def collect_server_api_info(self):
        """🚀 Server e API"""
        print("🚀 Analizzando server e API...")
        
        # Processi attivi
        output = self.run_command('ss -tuln 2>/dev/null | grep -E ":800[0-9]" || echo "Nessun server su porte 8000-8010"')
        self.append_to_files("PROCESSI ATTIVI (porta 8000-8010)", output)
        
        # File main/server
        output = self.run_command('find . -name "main.py" -o -name "app.py" -o -name "server.py" | head -5')
        self.append_to_files("FILE MAIN/SERVER", output)
        
        # Test connessione API
        api_test = self.run_command('curl -s http://127.0.0.1:8000/docs >/dev/null 2>&1 && echo "API 8000 raggiungibile" || echo "API 8000 non raggiungibile"')
        api_test += "\n" + self.run_command('curl -s http://127.0.0.1:8001/docs >/dev/null 2>&1 && echo "API 8001 raggiungibile" || echo "API 8001 non raggiungibile"')
        self.append_to_files("TEST CONNESSIONE API LOCALE", api_test)
        
        # Endpoint API esistenti
        openapi_output = self.run_command('curl -s http://127.0.0.1:8000/openapi.json | python -m json.tool | head -50')
        self.append_to_files("ENDPOINT API (OpenAPI)", openapi_output)
        
        # Contenuto main.py completo
        if os.path.exists("app/main.py"):
            content = self.run_command("cat app/main.py")
            self.append_to_files("CONTENUTO COMPLETO app/main.py", content)
        
        return {"server_api": "completed"}

    def collect_scripts_automation(self):
        """📋 Script e Automazione"""
        print("📋 Raccogliendo script...")
        
        # Script disponibili
        output = self.run_command('find . -name "*.py" | grep -E "(script|run|start|setup|import|crawl)" | head -10')
        self.append_to_files("SCRIPT DISPONIBILI", output)
        
        # File eseguibili
        output = self.run_command('find . -type f -executable -name "*.py" -o -name "*.sh" | head -10')
        self.append_to_files("FILE ESEGUIBILI", output)
        
        # Log directory
        log_check = '''
if [ -d logs ]; then
    echo "Directory logs trovata:"
    ls -la logs/ | head -10
else
    echo "Directory logs non trovata"
fi
        '''
        output = self.run_command(log_check)
        self.append_to_files("LOG DIRECTORY", output)
        
        return {"scripts": "completed"}

    def collect_system_status(self):
        """📊 Stato Sistema"""
        print("📊 Analizzando stato sistema...")
        
        # Ultimi log
        log_check = '''
if [ -f logs/app.log ]; then
    echo "Ultimi 5 log entries:"
    tail -5 logs/app.log
elif [ -f app.log ]; then
    echo "Ultimi 5 log entries:"
    tail -5 app.log
else
    echo "Nessun file log trovato"
fi
        '''
        output = self.run_command(log_check)
        self.append_to_files("ULTIMI LOG", output)
        
        # Dimensioni directory
        output = self.run_command("du -sh . 2>/dev/null")
        output += "\n" + self.run_command("du -sh */ 2>/dev/null | head -10")
        self.append_to_files("DIMENSIONI DIRECTORY PRINCIPALI", output)
        
        # Info sistema
        output = self.run_command("uname -a")
        self.append_to_files("INFO SISTEMA", output)
        
        # Spazio disco
        output = self.run_command("df -h | head -10")
        self.append_to_files("SPAZIO DISCO", output)
        
        # Memoria
        output = self.run_command("free -h")
        self.append_to_files("MEMORIA SISTEMA", output)
        
        return {"system_status": "completed"}

    def collect_key_file_contents(self):
        """🔍 Contenuto File Chiave"""
        print("🔍 Leggendo file chiave...")
        
        # Lista file chiave da analizzare
        key_files = [
            "app/main.py",
            "app/crud.py", 
            "app/core/database.py",
            ".env",
            "alembic.ini",
            "requirements.txt"
        ]
        
        for file_path in key_files:
            if os.path.exists(file_path):
                content = self.run_command(f"cat {file_path}")
                self.append_to_files(f"CONTENUTO COMPLETO {file_path}", content)
        
        # Templates HTML
        template_files = self.run_command('find app/templates -name "*.html" 2>/dev/null || echo ""').strip().split('\n')
        for template_file in template_files:
            if template_file and os.path.exists(template_file):
                content = self.run_command(f"cat {template_file}")
                self.append_to_files(f"TEMPLATE {template_file}", content)
        
        return {"key_files": "completed"}

    def collect_database_schema_analysis(self):
        """Analizza schema database in dettaglio"""
        print("🗄️ Analizzando schema database...")
        
        # Verifica tabelle database
        db_schema_check = '''
python -c "
try:
    import sys
    sys.path.append('.')
    from app.core.database import engine
    from sqlalchemy import inspect
    inspector = inspect(engine)
    print('Tabelle esistenti:', inspector.get_table_names())
    for table in inspector.get_table_names():
        print(f'\\n--- Tabella: {table} ---')
        columns = inspector.get_columns(table)
        for col in columns:
            print(f'  {col[\"name\"]}: {col[\"type\"]}')
except Exception as e:
    print(f'Errore analisi database: {e}')
"
        '''
        output = self.run_command(db_schema_check)
        self.append_to_files("ANALISI SCHEMA DATABASE", output)
        
        return {"database_schema": "completed"}

    def generate_comprehensive_documentation(self):
        """Genera la documentazione completa"""
        print("🚀 Generando documentazione completa per chatbot...")
        
        # Inizializza file con header
        header = f"""# AI Research Platform - Configurazione Completa
Generato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Timestamp: {self.timestamp}
Directory: {os.getcwd()}
"""
        
        with open(self.md_file, 'w', encoding='utf-8') as f:
            f.write(header)
        with open(self.txt_file, 'w', encoding='utf-8') as f:
            f.write(header)
        
        # Raccoglie tutte le informazioni
        collected_data = {}
        
        collected_data.update(self.collect_project_structure())
        collected_data.update(self.collect_configuration_setup())
        collected_data.update(self.collect_python_info())
        collected_data.update(self.collect_database_info())
        collected_data.update(self.collect_server_api_info())
        collected_data.update(self.collect_scripts_automation())
        collected_data.update(self.collect_system_status())
        collected_data.update(self.collect_key_file_contents())
        collected_data.update(self.collect_database_schema_analysis())
        
        # Salva JSON con metadati
        full_data = {
            "timestamp": self.timestamp,
            "generation_date": datetime.now().isoformat(),
            "platform_name": "AI Research Platform",
            "base_path": os.getcwd(),
            "collected_sections": collected_data,
            "files_generated": {
                "markdown": self.md_file,
                "text": self.txt_file,
                "json": self.json_file
            }
        }
        
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)
        
        # Genera istruzioni chatbot finali
        self.generate_chatbot_instructions()
        
        print(f"✅ Documentazione completa generata!")
        print(f"📁 Directory: {self.output_dir}/")
        print(f"📄 Markdown: {self.md_file}")
        print(f"📄 Text: {self.txt_file}")
        print(f"📄 JSON: {self.json_file}")
        print(f"🤖 Chatbot Instructions: {self.output_dir}/chatbot_instructions.md")
        
        return self.output_dir

    def generate_chatbot_instructions(self):
        """Genera istruzioni specifiche per chatbot"""
        instructions = f"""# ISTRUZIONI CHATBOT - AI Research Platform

## CONTESTO PIATTAFORMA
Sei un assistente specializzato per la "AI Research Platform", una piattaforma di ricerca avanzata.

## INFORMAZIONI TECNICHE COMPLETE
- **Generato**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Framework**: FastAPI (Python 3.13.3)
- **Database**: PostgreSQL
- **Deployment**: Ubuntu VM (192.168.1.20:8000)
- **Ambiente**: Virtual Environment attivo

## DOCUMENTI DI RIFERIMENTO
1. **platform_current_config.md** - Configurazione completa in formato Markdown
2. **platform_current_config.txt** - Configurazione completa in formato testo
3. **platform_complete_data.json** - Tutti i dati strutturati

## COME USARE QUESTI DOCUMENTI
- **Per domande tecniche**: Consulta platform_current_config.md per dettagli codice
- **Per troubleshooting**: Usa platform_current_config.txt per analisi sistema
- **Per sviluppo**: Riferisciti ai contenuti completi dei file sorgente inclusi

## ARCHITETTURA SISTEMA
- **Main app**: app/main.py (FastAPI application)
- **Models**: app/models/ (SQLAlchemy ORM)
- **Schemas**: app/schemas/ (Pydantic models)
- **CRUD**: app/crud.py (Database operations)
- **Templates**: app/templates/ (HTML frontend)

## FUNZIONALITÀ PRINCIPALI
1. **Dashboard**: Gestione progetti e statistiche
2. **API REST**: Endpoint completi per CRUD operations
3. **Ricerca Full-text**: Ricerca nei contenuti delle fonti
4. **Import Dati**: Upload e processamento Excel/CSV
5. **Database Relations**: Projects → Sources → Entities

## COME AIUTARE L'UTENTE
### Per sviluppo:
- Spiega architettura FastAPI/SQLAlchemy basandoti sui file sorgente inclusi
- Mostra endpoint API dal contenuto di app/main.py
- Guida implementazione nuove feature

### Per deployment:
- Verifica configurazione da .env e alembic.ini
- Troubleshoot connessioni database PostgreSQL
- Gestione virtual environment

### Per utilizzo:
- Guida navigazione dashboard dai template HTML
- Spiega funzioni API REST
- Assistenza import dati

## IMPORTANTE
RISPONDI SEMPRE BASANDOTI SUI DATI CONCRETI CONTENUTI NELLA DOCUMENTAZIONE GENERATA.
NON INVENTARE INFORMAZIONI - USA SOLO QUELLO CHE È DOCUMENTATO NEI FILE ALLEGATI.

## STATUS ATTUALE
La piattaforma è operativa e accessibile. Tutti i dettagli tecnici, configurazioni e codice sorgente sono documentati nei file allegati.
"""
        
        instructions_file = f"{self.output_dir}/chatbot_instructions.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

def main():
    """Funzione principale"""
    print("🚀 Enhanced AI Research Platform Documentation Generator")
    print("=" * 60)
    
    generator = EnhancedPlatformDocumentationGenerator()
    output_dir = generator.generate_comprehensive_documentation()
    
    print(f"\n📊 DOCUMENTAZIONE COMPLETA GENERATA!")
    print(f"📁 Directory output: {output_dir}")
    print(f"\n📋 File generati:")
    print(f"   📄 platform_current_config.md (formato Markdown)")
    print(f"   📄 platform_current_config.txt (formato testo)")  
    print(f"   📄 platform_complete_data.json (dati strutturati)")
    print(f"   🤖 chatbot_instructions.md (istruzioni AI)")
    
    print(f"\n🤖 PER ISTRUIRE UN CHATBOT:")
    print(f"   1. Carica il file chatbot_instructions.md")
    print(f"   2. Carica platform_current_config.md per dettagli tecnici")
    print(f"   3. Il chatbot avrà conoscenza completa della piattaforma!")

if __name__ == "__main__":
    main()
