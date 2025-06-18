# network_setup.py
"""
Configurazione per rendere la piattaforma accessibile dalla rete locale
"""

import os
import socket
import subprocess
from pathlib import Path

def get_vm_network_info():
    """Ottiene informazioni di rete della VM"""
    print("🔍 Rilevamento configurazione di rete...")
    
    # Ottieni IP locale
    try:
        # Connessione dummy per ottenere IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print(f"📍 IP VM rilevato: {local_ip}")
        
        # Verifica se è un IP privato
        if (local_ip.startswith('192.168.') or 
            local_ip.startswith('10.') or 
            local_ip.startswith('172.')):
            print("✅ IP privato valido per rete locale")
            return local_ip
        else:
            print("⚠️  IP pubblico rilevato - verifica configurazione")
            return local_ip
            
    except Exception as e:
        print(f"❌ Errore nel rilevamento IP: {e}")
        
        # Fallback: chiedi manualmente
        manual_ip = input("Inserisci l'IP della VM (es. 192.168.1.100): ")
        return manual_ip.strip()

def check_firewall_status():
    """Controlla stato firewall Ubuntu"""
    print("\n🔥 Controllo firewall...")
    
    try:
        result = subprocess.run(['sudo', 'ufw', 'status'], 
                              capture_output=True, text=True)
        
        if "Status: active" in result.stdout:
            print("🔥 UFW Firewall è ATTIVO")
            print("📋 Regole attuali:")
            print(result.stdout)
            return True
        else:
            print("✅ UFW Firewall è inattivo")
            return False
            
    except FileNotFoundError:
        print("ℹ️  UFW non installato")
        return False
    except Exception as e:
        print(f"⚠️  Errore controllo firewall: {e}")
        return False

def configure_firewall_rules(vm_ip):
    """Configura regole firewall per l'accesso di rete"""
    print(f"\n🔧 Configurazione firewall per IP {vm_ip}...")
    
    commands = [
        # Apri porta 8000 per FastAPI
        ['sudo', 'ufw', 'allow', '8000/tcp'],
        # Opzionale: apri porta 22 per SSH
        ['sudo', 'ufw', 'allow', '22/tcp'],
        # Opzionale: apri porta 5432 per PostgreSQL (solo se necessario)
        # ['sudo', 'ufw', 'allow', 'from', '192.168.0.0/16', 'to', 'any', 'port', '5432'],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Eseguito: {' '.join(cmd)}")
            else:
                print(f"⚠️  Errore: {' '.join(cmd)} - {result.stderr}")
        except Exception as e:
            print(f"❌ Errore esecuzione comando: {e}")
    
    # Ricarica firewall
    try:
        subprocess.run(['sudo', 'ufw', 'reload'], capture_output=True)
        print("🔄 Firewall ricaricato")
    except:
        pass

def update_fastapi_host_config():
    """Aggiorna la configurazione FastAPI per accettare connessioni esterne"""
    
    config_updates = {
        'host': '0.0.0.0',  # Ascolta su tutte le interfacce
        'port': 8000,
        'allow_origins': ["*"],  # Permetti CORS da qualsiasi origine
    }
    
    print("\n📝 Aggiornamento configurazione FastAPI...")
    
    # Cerca il file main.py
    main_py_path = Path("app/main.py")
    
    if not main_py_path.exists():
        print("❌ File app/main.py non trovato")
        return False
    
    # Leggi contenuto attuale
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Aggiungi configurazione CORS se non presente
    cors_config = '''
# === CONFIGURAZIONE RETE ===
from fastapi.middleware.cors import CORSMiddleware

# Configura CORS per accesso da rete locale
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, specifica gli IP della tua rete
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''
    
    if "CORSMiddleware" not in content:
        # Trova dove inserire la configurazione CORS
        app_creation_line = "app = FastAPI("
        
        if app_creation_line in content:
            # Inserisci dopo la creazione dell'app
            lines = content.split('\n')
            new_lines = []
            app_found = False
            
            for line in lines:
                new_lines.append(line)
                if app_creation_line in line and not app_found:
                    # Trova la fine della dichiarazione FastAPI
                    bracket_count = line.count('(') - line.count(')')
                    i = len(new_lines)
                    
                    while bracket_count > 0 and i < len(lines):
                        if i < len(lines):
                            bracket_count += lines[i].count('(') - lines[i].count(')')
                        i += 1
                    
                    # Inserisci CORS config dopo
                    new_lines.extend(cors_config.strip().split('\n'))
                    app_found = True
            
            content = '\n'.join(new_lines)
        else:
            # Aggiungi alla fine del file
            content += cors_config
    
    # Salva il file aggiornato
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Configurazione CORS aggiunta")
    return True

def create_network_startup_script(vm_ip):
    """Crea script per avviare il server con configurazione di rete"""
    
    startup_script = f'''#!/bin/bash
# start_server_network.sh - Avvia server per accesso di rete

echo "🚀 Avvio AI Research Platform per rete locale"
echo "📍 IP VM: {vm_ip}"
echo "🌐 URL accesso: http://{vm_ip}:8000"
echo "======================================"

# Attiva virtual environment
source venv/bin/activate

# Avvia FastAPI con host 0.0.0.0
echo "📡 Avvio server FastAPI su tutte le interfacce..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ Server avviato!"
echo "🌐 Accesso da rete locale: http://{vm_ip}:8000"
echo "📱 Dashboard: http://{vm_ip}:8000/dashboard"
echo "📚 API Docs: http://{vm_ip}:8000/docs"
'''
    
    script_path = Path("start_server_network.sh")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    # Rendi eseguibile
    os.chmod(script_path, 0o755)
    
    print(f"✅ Script creato: {script_path}")
    return script_path

def update_frontend_urls(vm_ip):
    """Aggiorna gli URL nel frontend per usare l'IP della VM"""
    
    print(f"\n🔧 Aggiornamento URL frontend per IP {vm_ip}...")
    
    # Pattern di sostituzione per i template
    url_replacements = {
        'http://127.0.0.1:8000': f'http://{vm_ip}:8000',
        'http://localhost:8000': f'http://{vm_ip}:8000',
        'const API_BASE_URL = window.location.origin': f'const API_BASE_URL = "http://{vm_ip}:8000"'
    }
    
    # Aggiorna template se esistono
    templates_dir = Path("app/templates")
    if templates_dir.exists():
        for template_file in templates_dir.glob("*.html"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Applica sostituzioni
                for old_url, new_url in url_replacements.items():
                    content = content.replace(old_url, new_url)
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Aggiornato: {template_file}")
            except Exception as e:
                print(f"⚠️  Errore aggiornamento {template_file}: {e}")

def test_network_connectivity(vm_ip):
    """Testa la connettività di rete"""
    print(f"\n🧪 Test connettività di rete...")
    
    # Test 1: Verifica porta 8000 in ascolto
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(5)
        result = test_socket.connect_ex((vm_ip, 8000))
        test_socket.close()
        
        if result == 0:
            print("✅ Porta 8000 in ascolto")
        else:
            print("❌ Porta 8000 non accessibile")
            
    except Exception as e:
        print(f"⚠️  Errore test porta: {e}")
    
    # Test 2: Suggerimenti per test da altri dispositivi
    print(f"\n📱 Per testare da altri dispositivi nella rete:")
    print(f"1. Browser: http://{vm_ip}:8000/dashboard")
    print(f"2. Ping: ping {vm_ip}")
    print(f"3. Telnet: telnet {vm_ip} 8000")

def create_network_info_file(vm_ip):
    """Crea file con informazioni di rete"""
    
    info_content = f"""
# 🌐 AI Research Platform - Informazioni Accesso di Rete

## 📍 Configurazione VM
- **IP Virtuale Machine**: {vm_ip}
- **Porta API**: 8000
- **Sistema**: Ubuntu su Proxmox

## 🔗 URL di Accesso dalla Rete Locale

### 🖥️ Interfacce Web
- **Dashboard**: http://{vm_ip}:8000/dashboard
- **Gestione Progetti**: http://{vm_ip}:8000/projects/view
- **Ricerca**: http://{vm_ip}:8000/search/view
- **Importazione**: http://{vm_ip}:8000/import
- **API Documentation**: http://{vm_ip}:8000/docs

### 🔌 Endpoint API
- **Base URL**: http://{vm_ip}:8000
- **Ricerca**: http://{vm_ip}:8000/search/?q=termine
- **Progetti**: http://{vm_ip}:8000/projects/
- **Statistiche**: http://{vm_ip}:8000/api/stats

## 📱 Test di Connettività

### Da Terminale (Linux/Mac/Windows)
```bash
# Test ping
ping {vm_ip}

# Test porta
telnet {vm_ip} 8000
# oppure
nc -zv {vm_ip} 8000

# Test HTTP
curl http://{vm_ip}:8000/api/stats
```

### Da Browser
1. Apri: http://{vm_ip}:8000/dashboard
2. Verifica che carichi la dashboard
3. Testa la ricerca e navigazione

## 🔧 Risoluzione Problemi

### Se non raggiungibile dalla rete:
1. **Firewall VM**: `sudo ufw status`
2. **Firewall Router**: Controlla impostazioni router
3. **Processo FastAPI**: `ps aux | grep uvicorn`
4. **Porta in ascolto**: `netstat -tuln | grep 8000`

### Comandi Utili
```bash
# Riavvia server per rete
./start_server_network.sh

# Controlla log
tail -f logs/app.log

# Verifica IP
ip addr show
```

## 📞 Accesso da Dispositivi

### Computer Windows/Mac/Linux
- Browser: http://{vm_ip}:8000/dashboard
- PowerShell: `Test-NetConnection {vm_ip} -Port 8000`

### Smartphone/Tablet
- Browser mobile: http://{vm_ip}:8000/dashboard
- App API client con base URL: http://{vm_ip}:8000

### Altri Dispositivi IoT
- HTTP GET: http://{vm_ip}:8000/api/stats
- WebSocket: ws://{vm_ip}:8000/ws (se implementato)

## 🔒 Sicurezza

**IMPORTANTE**: Questo setup è per rete locale privata.
Per accesso internet pubblico, implementa:
- HTTPS/SSL
- Autenticazione utenti
- Firewall specifico per IP
- Rate limiting
- VPN access

---
Generato automaticamente il {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open("NETWORK_ACCESS_INFO.md", 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print("📄 File informazioni creato: NETWORK_ACCESS_INFO.md")

def main():
    """Configurazione completa per accesso di rete"""
    print("🌐 CONFIGURAZIONE ACCESSO DI RETE")
    print("=" * 50)
    
    # 1. Rileva IP
    vm_ip = get_vm_network_info()
    
    # 2. Controlla firewall
    firewall_active = check_firewall_status()
    
    # 3. Configura firewall se necessario
    if firewall_active:
        response = input(f"\n🔥 Configurare firewall per permettere accesso sulla porta 8000? (s/n): ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            configure_firewall_rules(vm_ip)
    
    # 4. Aggiorna configurazione FastAPI
    update_fastapi_host_config()
    
    # 5. Crea script di avvio
    script_path = create_network_startup_script(vm_ip)
    
    # 6. Aggiorna URL frontend
    update_frontend_urls(vm_ip)
    
    # 7. Crea file informazioni
    create_network_info_file(vm_ip)
    
    # 8. Test connettività
    test_network_connectivity(vm_ip)
    
    print("\n" + "=" * 50)
    print("🎉 CONFIGURAZIONE RETE COMPLETATA!")
    print("=" * 50)
    print(f"\n📍 IP VM: {vm_ip}")
    print(f"🌐 URL Dashboard: http://{vm_ip}:8000/dashboard")
    print(f"📚 API Docs: http://{vm_ip}:8000/docs")
    
    print(f"\n🚀 Per avviare il server:")
    print(f"   ./{script_path}")
    print(f"   # oppure")
    print(f"   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    
    print(f"\n📱 Test da altri dispositivi:")
    print(f"   Browser: http://{vm_ip}:8000/dashboard")
    print(f"   Ping: ping {vm_ip}")
    
    print(f"\n📄 Info complete in: NETWORK_ACCESS_INFO.md")

if __name__ == "__main__":
    main()
