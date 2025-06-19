#!/usr/bin/env python3
"""
Ultimate AI Research Platform Documentation Generator
Genera documentazione completa con struttura dettagliata, inventari e analisi approfondite
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import re

class UltimatePlatformDocumentationGenerator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"platform_docs_ultimate_{self.timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # File di output
        self.md_file = f"{self.output_dir}/platform_complete_structure.md"
        self.txt_file = f"{self.output_dir}/platform_complete_structure.txt"
        self.json_file = f"{self.output_dir}/platform_complete_data.json"
        self.tree_file = f"{self.output_dir}/directory_tree.txt"
        self.inventory_file = f"{self.output_dir}/file_inventory.json"
        
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
            f.write(f"\n{'='*80}\n{section_title}\n{'='*80}\n{content}\n")

    def generate_directory_tree(self):
        """📁 Genera struttura ad albero completa"""
        print("🌳 Generando struttura ad albero completa...")
        
        # Tree command (se disponibile)
        tree_output = self.run_command("tree -a -L 4 --dirsfirst --charset ascii 2>/dev/null || echo 'tree command not available'")
        
        # Alternativa con find se tree non disponibile
        if "tree command not available" in tree_output:
            tree_output = self.run_command("""
find . -type d | head -50 | sed 's|[^/]*/|  |g' | sed 's|  \\([^/]*\\)$|-- \\1|'
echo ""
echo "=== FILE PRINCIPALI ==="
find . -name "*.py" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.md" | head -30 | sort
            """)
        
        self.append_to_files("STRUTTURA DIRECTORY AD ALBERO", tree_output)
        
        # Salva in file separato
        with open(self.tree_file, 'w', encoding='utf-8') as f:
            f.write(tree_output)
        
        return {"directory_tree": "completed"}

    def create_file_inventory(self):
        """📋 Crea inventario completo file per tipo"""
        print("📋 Creando inventario file completo...")
        
        inventory = {
            "python_files": [],
            "html_templates": [],
            "css_files": [],
            "javascript_files": [],
            "markdown_files": [],
            "config_files": [],
            "data_files": [],
            "script_files": [],
            "image_files": [],
            "other_files": []
        }
        
        # Scansiona tutti i file
        for root, dirs, files in os.walk('.'):
            # Skip venv directory per evitare troppi file
            if 'venv' in root:
                continue
                
            for file in files:
                filepath = os.path.join(root, file)
                file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                
                file_info = {
                    "path": filepath,
                    "size": file_size,
                    "size_human": self.format_bytes(file_size)
                }
                
                # Categorizza per estensione
                if file.endswith('.py'):
                    inventory["python_files"].append(file_info)
                elif file.endswith(('.html', '.htm')):
                    inventory["html_templates"].append(file_info)
                elif file.endswith('.css'):
                    inventory["css_files"].append(file_info)
                elif file.endswith('.js'):
                    inventory["javascript_files"].append(file_info)
                elif file.endswith(('.md', '.rst', '.txt')):
                    inventory["markdown_files"].append(file_info)
                elif file.endswith(('.env', '.ini', '.cfg', '.conf', '.toml', '.yaml', '.yml')):
                    inventory["config_files"].append(file_info)
                elif file.endswith(('.json', '.xlsx', '.xls', '.csv')):
                    inventory["data_files"].append(file_info)
                elif file.endswith(('.sh', '.bat')):
                    inventory["script_files"].append(file_info)
                elif file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
                    inventory["image_files"].append(file_info)
                else:
                    inventory["other_files"].append(file_info)
        
        # Ordina per dimensione
        for category in inventory:
            inventory[category].sort(key=lambda x: x["size"], reverse=True)
        
        # Genera statistiche
        stats = {}
        for category, files in inventory.items():
            stats[category] = {
                "count": len(files),
                "total_size": sum(f["size"] for f in files),
                "total_size_human": self.format_bytes(sum(f["size"] for f in files))
            }
        
        inventory["statistics"] = stats
        
        # Salva inventario JSON
        with open(self.inventory_file, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)
        
        # Crea summary per documentazione
        summary = "INVENTARIO FILE PER CATEGORIA\\n\\n"
        for category, stat in stats.items():
            category_name = category.replace('_', ' ').title()
            summary += f"{category_name}: {stat['count']} file ({stat['total_size_human']})\\n"
        
        summary += "\\n=== FILE PIU' GRANDI ===\\n"
        all_files = []
        for files in inventory.values():
            if isinstance(files, list):
                all_files.extend(files)
        all_files.sort(key=lambda x: x["size"], reverse=True)
        
        for file in all_files[:10]:
            summary += f"{file['path']}: {file['size_human']}\\n"
        
        self.append_to_files("INVENTARIO FILE COMPLETO", summary)
        
        return {"file_inventory": "completed"}

    def analyze_python_structure(self):
        """🐍 Analizza struttura Python in dettaglio"""
        print("🐍 Analizzando struttura Python...")
        
        analysis = {
            "modules": {},
            "imports": {},
            "classes": {},
            "functions": {},
            "dependencies": []
        }
        
        python_files = []
        for root, dirs, files in os.walk('.'):
            if 'venv' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                module_analysis = {
                    "imports": self.extract_imports(content),
                    "classes": self.extract_classes(content),
                    "functions": self.extract_functions(content),
                    "lines": len(content.split('\\n')),
                    "size": len(content)
                }
                
                analysis["modules"][py_file] = module_analysis
                
            except Exception as e:
                analysis["modules"][py_file] = {"error": str(e)}
        
        # Genera summary
        summary = f"ANALISI STRUTTURA PYTHON\\n\\n"
        summary += f"Moduli Python totali: {len(python_files)}\\n"
        summary += f"Linee di codice totali: {sum(m.get('lines', 0) for m in analysis['modules'].values())}\\n\\n"
        
        summary += "=== MODULI PRINCIPALI ===\\n"
        for module, data in analysis["modules"].items():
            if not isinstance(data, dict) or 'error' in data:
                continue
            summary += f"{module}: {data['lines']} linee, {len(data['classes'])} classi, {len(data['functions'])} funzioni\\n"
        
        summary += "\\n=== IMPORT PIU' COMUNI ===\\n"
        all_imports = []
        for module_data in analysis["modules"].values():
            if isinstance(module_data, dict) and 'imports' in module_data:
                all_imports.extend(module_data['imports'])
        
        import_counts = {}
        for imp in all_imports:
            import_counts[imp] = import_counts.get(imp, 0) + 1
        
        for imp, count in sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            summary += f"{imp}: {count} volte\\n"
        
        self.append_to_files("ANALISI STRUTTURA PYTHON", summary)
        
        return {"python_analysis": "completed"}

    def analyze_frontend_structure(self):
        """🎨 Analizza struttura frontend"""
        print("🎨 Analizzando struttura frontend...")
        
        frontend_analysis = {
            "templates": {},
            "static_files": {},
            "routes": []
        }
        
        # Analizza template HTML
        for root, dirs, files in os.walk('./app/templates'):
            for file in files:
                if file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        frontend_analysis["templates"][filepath] = {
                            "size": len(content),
                            "lines": len(content.split('\\n')),
                            "forms": content.count('<form'),
                            "scripts": content.count('<script'),
                            "links": content.count('<a '),
                            "includes": len(re.findall(r'{%\\s*include', content)),
                            "blocks": len(re.findall(r'{%\\s*block', content))
                        }
                    except:
                        frontend_analysis["templates"][filepath] = {"error": "Cannot read file"}
        
        # Analizza file statici
        static_dirs = ['./app/static', './static']
        for static_dir in static_dirs:
            if os.path.exists(static_dir):
                for root, dirs, files in os.walk(static_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        file_size = os.path.getsize(filepath)
                        frontend_analysis["static_files"][filepath] = {
                            "size": file_size,
                            "size_human": self.format_bytes(file_size),
                            "type": file.split('.')[-1] if '.' in file else 'unknown'
                        }
        
        # Estrai route da main.py
        try:
            with open('./app/main.py', 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            routes = re.findall(r'@app\\.(get|post|put|delete)\\("([^"]+)"', main_content)
            frontend_analysis["routes"] = [{"method": method.upper(), "path": path} for method, path in routes]
        except:
            frontend_analysis["routes"] = []
        
        # Genera summary
        summary = "ANALISI STRUTTURA FRONTEND\\n\\n"
        summary += f"Template HTML: {len(frontend_analysis['templates'])}\\n"
        summary += f"File statici: {len(frontend_analysis['static_files'])}\\n"
        summary += f"Route API: {len(frontend_analysis['routes'])}\\n\\n"
        
        summary += "=== TEMPLATE DETAILS ===\\n"
        for template, data in frontend_analysis["templates"].items():
            if 'error' not in data:
                summary += f"{template}: {data['lines']} linee, {data['forms']} form, {data['blocks']} block\\n"
        
        summary += "\\n=== ROUTE API ===\\n"
        for route in frontend_analysis["routes"]:
            summary += f"{route['method']} {route['path']}\\n"
        
        self.append_to_files("ANALISI STRUTTURA FRONTEND", summary)
        
        return {"frontend_analysis": "completed"}

    def collect_original_analysis(self):
        """Mantiene l'analisi originale per compatibilità"""
        print("📊 Aggiungendo analisi originale...")
        
        # Configurazione
        output = self.run_command('ls -la | grep -E "\\\\.(env|cfg|ini|toml|yaml|yml|conf)$"')
        self.append_to_files("FILE CONFIGURAZIONE", output)
        
        # Python info
        output = self.run_command("pip list --format=freeze")
        self.append_to_files("PIP LIST COMPLETA", output)
        
        # Contenuti file chiave
        key_files = ["app/main.py", "app/crud.py", "app/core/database.py", ".env"]
        for file_path in key_files:
            if os.path.exists(file_path):
                content = self.run_command(f"cat {file_path}")
                self.append_to_files(f"CONTENUTO COMPLETO {file_path}", content)
        
        # Template
        template_files = self.run_command('find app/templates -name "*.html" 2>/dev/null || echo ""').strip().split('\\n')
        for template_file in template_files:
            if template_file and template_file.strip() and os.path.exists(template_file.strip()):
                content = self.run_command(f"cat {template_file.strip()}")
                self.append_to_files(f"TEMPLATE {template_file.strip()}", content)
        
        return {"original_analysis": "completed"}

    def generate_ultimate_documentation(self):
        """Genera la documentazione ultimate completa"""
        print("🚀 Generando documentazione ULTIMATE completa...")
        
        # Header
        header = f"""# AI Research Platform - Documentazione ULTIMATE Completa
Generato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Timestamp: {self.timestamp}
Directory: {os.getcwd()}
Tipo: Analisi completa con struttura dettagliata, inventari e dipendenze

"""
        
        with open(self.md_file, 'w', encoding='utf-8') as f:
            f.write(header)
        with open(self.txt_file, 'w', encoding='utf-8') as f:
            f.write(header)
        
        # Esegui tutte le analisi
        collected_data = {}
        
        # 1. Struttura directory
        collected_data.update(self.generate_directory_tree())
        
        # 2. Inventario file
        collected_data.update(self.create_file_inventory())
        
        # 3. Analisi Python
        collected_data.update(self.analyze_python_structure())
        
        # 4. Analisi Frontend
        collected_data.update(self.analyze_frontend_structure())
        
        # 5. Analisi originale (compatibilità)
        collected_data.update(self.collect_original_analysis())
        
        # Salva dati completi JSON
        full_data = {
            "timestamp": self.timestamp,
            "generation_date": datetime.now().isoformat(),
            "platform_name": "AI Research Platform",
            "base_path": os.getcwd(),
            "analysis_type": "ULTIMATE_COMPLETE",
            "collected_sections": collected_data
        }
        
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)
        
        # Genera istruzioni chatbot ultimate
        self.generate_ultimate_chatbot_instructions()
        
        print(f"✅ Documentazione ULTIMATE generata!")
        print(f"📁 Directory: {self.output_dir}/")
        print(f"📄 Markdown: {self.md_file}")
        print(f"📄 Text: {self.txt_file}")
        print(f"📄 JSON: {self.json_file}")
        print(f"🌳 Tree: {self.tree_file}")
        print(f"📋 Inventory: {self.inventory_file}")
        print(f"🤖 Chatbot Instructions: {self.output_dir}/ultimate_chatbot_instructions.md")
        
        return self.output_dir

    def generate_ultimate_chatbot_instructions(self):
        """Genera istruzioni ultimate per chatbot"""
        instructions = f"""# ISTRUZIONI CHATBOT ULTIMATE - AI Research Platform

## CONTESTO PIATTAFORMA
Sei un assistente specializzato ESPERTO della "AI Research Platform", una piattaforma di ricerca avanzata.

## INFORMAZIONI TECNICHE ULTIMATE
- **Generato**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Framework**: FastAPI (Python 3.13.3)
- **Database**: PostgreSQL
- **Deployment**: Ubuntu VM (192.168.1.20:8000)

## DOCUMENTI DISPONIBILI (ULTIMATE SET)
1. **platform_complete_structure.md** - Documentazione ultimate completa
2. **directory_tree.txt** - Struttura directory completa ad albero
3. **file_inventory.json** - Inventario completo tutti i file per categoria

## FUNZIONALITÀ ULTIMATE
- 🌳 Struttura directory completa ad albero
- 📊 Inventario file per categoria con dimensioni
- 🐍 Analisi Python: moduli, classi, funzioni, import
- 🎨 Analisi Frontend: template, route, static files

RISPONDI SEMPRE COME UN ESPERTO che conosce OGNI DETTAGLIO del sistema!
"""
        
        instructions_file = f"{self.output_dir}/ultimate_chatbot_instructions.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

    def extract_imports(self, content):
        """Estrae import da codice Python"""
        imports = []
        if content:
            lines = content.split('\\n')
            for line in lines[:50]:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
        return imports

    def extract_classes(self, content):
        """Estrae definizioni classi"""
        classes = []
        if content:
            matches = re.findall(r'class\\s+(\\w+).*?:', content)
            classes = matches
        return classes

    def extract_functions(self, content):
        """Estrae definizioni funzioni"""
        functions = []
        if content:
            matches = re.findall(r'def\\s+(\\w+)\\s*\\(', content)
            functions = matches
        return functions

    def format_bytes(self, bytes_size):
        """Formatta bytes in formato human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f}TB"

def main():
    generator = UltimatePlatformDocumentationGenerator()
    output_dir = generator.generate_ultimate_documentation()
    
    print(f"\\n🎉 DOCUMENTAZIONE ULTIMATE COMPLETATA!")
    print(f"📁 Directory output: {output_dir}")
    print(f"\\n📋 File generati ULTIMATE:")
    print(f"   📄 platform_complete_structure.md (documentazione completa)")
    print(f"   📄 platform_complete_structure.txt (formato testo)")  
    print(f"   📄 platform_complete_data.json (dati strutturati)")
    print(f"   🌳 directory_tree.txt (struttura ad albero)")
    print(f"   📋 file_inventory.json (inventario completo file)")
    print(f"   🤖 ultimate_chatbot_instructions.md (istruzioni AI ultimate)")
    
    print(f"\\n🤖 PER ISTRUIRE UN CHATBOT ULTIMATE:")
    print(f"   1. Carica ultimate_chatbot_instructions.md")
    print(f"   2. Carica platform_complete_structure.md per dettagli")
    print(f"   3. Il chatbot avrà conoscenza ULTIMATE della piattaforma!")

if __name__ == "__main__":
    main()
