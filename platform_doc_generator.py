#!/usr/bin/env python3
"""
AI Research Platform Documentation Generator
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class PlatformDocumentationGenerator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"platform_docs_{self.timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def run_command(self, command):
        """Esegue comando e restituisce output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    def collect_platform_info(self):
        """Raccoglie informazioni complete della piattaforma"""
        print("🔍 Raccogliendo informazioni della piattaforma...")
        
        info = {
            "timestamp": self.timestamp,
            "python_version": self.run_command("python --version"),
            "directory_structure": self.run_command("ls -la"),
            "python_files": self.run_command("find . -name '*.py' | head -20"),
            "api_status": self.run_command("curl -s http://127.0.0.1:8000/docs >/dev/null 2>&1 && echo 'RUNNING' || echo 'NOT RUNNING'"),
            "database_status": self.run_command("ps aux | grep postgres | grep -v grep || echo 'PostgreSQL not running'")
        }
        
        # Legge file principali
        files_to_read = ["app/main.py", ".env", "app/models/project.py"]
        for file_path in files_to_read:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        info[f"content_{file_path.replace('/', '_')}"] = f.read()[:2000]  # Prime 2000 caratteri
                except:
                    info[f"content_{file_path.replace('/', '_')}"] = "File not readable"
        
        return info

    def generate_documentation(self):
        """Genera la documentazione completa"""
        print("📝 Generando documentazione...")
        
        info = self.collect_platform_info()
        
        # Salva JSON completo
        json_file = f"{self.output_dir}/platform_info.json"
        with open(json_file, 'w') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        # Crea istruzioni per chatbot
        chatbot_instructions = f"""# CHATBOT INSTRUCTIONS - AI Research Platform

## PLATFORM OVERVIEW
- **Name**: AI Research Platform
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Access**: http://192.168.1.20:8000
- **Status**: {info['api_status']}
- **Python**: {info['python_version']}

## KEY INFORMATION
- Generated: {info['timestamp']}
- Main app: app/main.py
- Models: app/models/
- Templates: app/templates/

## HOW TO HELP USERS
1. For development questions: Explain FastAPI structure
2. For deployment: Guide server startup and troubleshooting  
3. For usage: Explain dashboard and API features

## CURRENT STATUS
- API Server: {info['api_status']}
- Database: {info['database_status']}
"""
        
        instructions_file = f"{self.output_dir}/chatbot_instructions.md"
        with open(instructions_file, 'w') as f:
            f.write(chatbot_instructions)
        
        print(f"✅ Documentazione creata in: {self.output_dir}/")
        print(f"📄 File JSON: {json_file}")
        print(f"🤖 Istruzioni chatbot: {instructions_file}")
        
        return self.output_dir

def main():
    generator = PlatformDocumentationGenerator()
    output_dir = generator.generate_documentation()
    
    print(f"\n🎉 COMPLETATO!")
    print(f"📁 Directory: {output_dir}")
    print(f"📊 Usa questi file per istruire il chatbot!")

if __name__ == "__main__":
    main()
