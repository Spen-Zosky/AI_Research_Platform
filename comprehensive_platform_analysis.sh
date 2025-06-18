#!/bin/bash
# comprehensive_platform_analysis.sh
# Framework completo per analisi piattaforma su VM Proxmox
# Versione: 2.0 - Ottimizzato per accesso di rete

echo "🚀 ANALISI COMPLETA PIATTAFORMA AI RESEARCH PLATFORM"
echo "===================================================="
echo "Data: $(date)"
echo "Host: $(hostname)"
echo "User: $(whoami)"
echo "Directory: $(pwd)"
echo "===================================================="

# === 🌐 INFORMAZIONI DI RETE COMPLETE ===
echo -e "\n🌐 === CONFIGURAZIONE DI RETE ==="
echo "--- Interfacce di rete ---"
ip addr show | grep -E "(inet |mtu|state)" | sed 's/^/  /'

echo -e "\n--- IP principale della VM ---"
VM_IP=$(ip route get 8.8.8.8 | awk '{print $7; exit}')
echo "  IP VM rilevato: $VM_IP"
echo "  Interfaccia di rete: $(ip route get 8.8.8.8 | awk '{print $5; exit}')"

echo -e "\n--- Gateway e routing ---"
echo "  Gateway predefinito: $(ip route | grep default | awk '{print $3}')"
echo "  Rete locale: $(ip route | grep 'scope link' | head -1 | awk '{print $1}')"

echo -e "\n--- Test connettività esterna ---"
ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "  ✅ Connessione internet OK" || echo "  ❌ Problema connessione internet"
ping -c 1 $(ip route | grep default | awk '{print $3}') >/dev/null 2>&1 && echo "  ✅ Gateway raggiungibile" || echo "  ❌ Gateway non raggiungibile"

echo -e "\n--- DNS configurazione ---"
echo "  Server DNS:"
grep nameserver /etc/resolv.conf | sed 's/^/    /'

# === 🔥 FIREWALL E SICUREZZA ===
echo -e "\n🔥 === FIREWALL E SICUREZZA ==="
echo "--- Stato UFW ---"
if command -v ufw >/dev/null 2>&1; then
    sudo ufw status 2>/dev/null | sed 's/^/  /' || echo "  UFW non configurato o errore accesso"
else
    echo "  UFW non installato"
fi

echo -e "\n--- Porte in ascolto (focus web services) ---"
if command -v netstat >/dev/null 2>&1; then
    netstat -tuln | grep -E ":(80|443|8000|8001|8080|3000|5000|5432)" | sed 's/^/  /'
else
    ss -tuln | grep -E ":(80|443|8000|8001|8080|3000|5000|5432)" | sed 's/^/  /' 2>/dev/null || echo "  Comando ss non disponibile"
fi

echo -e "\n--- Servizi attivi su porte web ---"
for port in 8000 8001 8080 3000 5000; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        process=$(lsof -Pi :$port -sTCP:LISTEN | tail -1 | awk '{print $1 " (PID:" $2 ")"}')
        echo "  ✅ Porta $port: $process"
    else
        echo "  ⚪ Porta $port: libera"
    fi
done

# === 📊 STATO SISTEMA VM PROXMOX ===
echo -e "\n📊 === STATO SISTEMA VM PROXMOX ==="
echo "--- Informazioni VM ---"
echo "  Hostname: $(hostname -f)"
echo "  Kernel: $(uname -r)"
echo "  OS: $(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "  Architettura: $(uname -m)"

echo -e "\n--- Risorse sistema ---"
echo "  CPU: $(nproc) core(s)"
echo "  RAM totale: $(free -h | awk 'NR==2{print $2}')"
echo "  RAM usata: $(free -h | awk 'NR==2{print $3}') ($(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}'))"
echo "  Swap: $(free -h | awk 'NR==3{print $2}') totale, $(free -h | awk 'NR==3{print $3}') usata"

echo -e "\n--- Storage ---"
echo "  Spazio disco principale:"
df -h / | tail -1 | awk '{print "    Totale: " $2 ", Usato: " $3 " (" $5 "), Disponibile: " $4}'

echo -e "\n--- Load average ---"
echo "  $(uptime | sed 's/.*load average: /  Carico sistema: /')"

echo -e "\n--- Processi principali (CPU) ---"
ps aux --sort=-%cpu | head -6 | tail -5 | awk '{print "  " $11 " (CPU:" $3 "%, MEM:" $4 "%, PID:" $2 ")"}' 2>/dev/null || echo "  Errore nel recupero processi"

# === 📁 STRUTTURA PROGETTO AVANZATA ===
echo -e "\n📁 === STRUTTURA PROGETTO AVANZATA ==="
echo "--- Directory principale ---"
ls -la | sed 's/^/  /'

echo -e "\n--- Struttura ad albero (3 livelli) ---"
if command -v tree >/dev/null 2>&1; then
    tree -L 3 -I '__pycache__|*.pyc|venv|.git' | head -20 | sed 's/^/  /'
else
    find . -maxdepth 3 -type d | grep -v -E '(__pycache__|\.git|venv)' | head -15 | sed 's/^/  /'
fi

echo -e "\n--- File Python per categoria ---"
echo "  Script principali:"
find . -name "*.py" -type f | grep -v -E '(venv|__pycache__|\.git)' | grep -E "(main|app|server|run)" | head -5 | sed 's/^/    /'

echo "  Modelli e schema:"
find . -name "*.py" -type f | grep -v -E '(venv|__pycache__|\.git)' | grep -E "(model|schema)" | head -5 | sed 's/^/    /'

echo "  Script di automazione:"
find . -name "*.py" -type f | grep -v -E '(venv|__pycache__|\.git)' | grep -E "(script|crawl|import|setup)" | head -5 | sed 's/^/    /'

echo -e "\n--- File di configurazione ---"
find . -maxdepth 2 \( -name "*.env" -o -name "*.cfg" -o -name "*.ini" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" -o -name "requirements.txt" -o -name "pyproject.toml" \) 2>/dev/null | sed 's/^/  /'

# === 🐍 AMBIENTE PYTHON DETTAGLIATO ===
echo -e "\n🐍 === AMBIENTE PYTHON DETTAGLIATO ==="
echo "--- Versioni Python ---"
echo "  Python: $(python --version 2>&1)"
python3 --version >/dev/null 2>&1 && echo "  Python3: $(python3 --version)" || echo "  Python3: non trovato"

echo -e "\n--- Virtual Environment ---"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "  ✅ Virtual environment attivo: $VIRTUAL_ENV"
    echo "  Python utilizzato: $(which python)"
    echo "  Pip utilizzato: $(which pip)"
else
    echo "  ⚠️  Virtual environment NON attivo"
    echo "  Python sistema: $(which python)"
fi

echo -e "\n--- Pacchetti framework web ---"
echo "  Framework installati:"
pip list 2>/dev/null | grep -iE "(fastapi|flask|django|starlette|uvicorn|gunicorn)" | sed 's/^/    /' || echo "    Nessun framework web trovato"

echo -e "\n--- Pacchetti database ---"
echo "  Database drivers:"
pip list 2>/dev/null | grep -iE "(psycopg|sqlalchemy|mysql|sqlite|redis)" | sed 's/^/    /' || echo "    Nessun driver database trovato"

echo -e "\n--- Pacchetti data science ---"
echo "  Data science:"
pip list 2>/dev/null | grep -iE "(pandas|numpy|scipy|sklearn|tensorflow|torch)" | sed 's/^/    /' || echo "    Nessun pacchetto data science trovato"

# === 🗄️ DATABASE E STORAGE ===
echo -e "\n🗄️ === DATABASE E STORAGE ==="
echo "--- Processi database attivi ---"
ps aux | grep -E "(postgres|mysql|redis|mongo)" | grep -v grep | awk '{print "  " $11 " (PID:" $2 ", CPU:" $3 "%)"}' || echo "  Nessun processo database trovato"

echo -e "\n--- Connessioni database (se PostgreSQL) ---"
if pgrep postgres >/dev/null; then
    echo "  ✅ PostgreSQL attivo"
    sudo -u postgres psql -c "SELECT count(*) as connessioni_attive FROM pg_stat_activity;" 2>/dev/null | grep -E "[0-9]+" | sed 's/^/    /' || echo "    Errore accesso PostgreSQL"
else
    echo "  ⚪ PostgreSQL non in esecuzione"
fi

echo -e "\n--- File database locali ---"
find . -name "*.db" -o -name "*.sqlite*" 2>/dev/null | head -5 | sed 's/^/  /' || echo "  Nessun file database locale trovato"

# === 🚀 SERVIZI WEB E API ===
echo -e "\n🚀 === SERVIZI WEB E API ==="
echo "--- Test connettività API locale ---"
for port in 8000 8001 8080; do
    if curl -s --max-time 3 http://127.0.0.1:$port/ >/dev/null 2>&1; then
        echo "  ✅ http://127.0.0.1:$port/ - RAGGIUNGIBILE"
    else
        echo "  ❌ http://127.0.0.1:$port/ - NON RAGGIUNGIBILE"
    fi
done

echo -e "\n--- Test accesso da rete (IP: $VM_IP) ---"
for port in 8000 8001 8080; do
    if timeout 3 bash -c "echo >/dev/tcp/$VM_IP/$port" 2>/dev/null; then
        echo "  ✅ http://$VM_IP:$port/ - PORTA APERTA"
    else
        echo "  ❌ http://$VM_IP:$port/ - PORTA CHIUSA/FILTRATA"
    fi
done

echo -e "\n--- Endpoint API (se FastAPI su 8000) ---"
if curl -s --max-time 5 http://127.0.0.1:8000/openapi.json >/dev/null 2>&1; then
    echo "  ✅ FastAPI operativo su porta 8000"
    echo "  Endpoint disponibili:"
    curl -s http://127.0.0.1:8000/openapi.json | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    paths = list(data.get('paths', {}).keys())
    for path in paths[:8]:
        print('    ' + path)
    if len(paths) > 8:
        print('    ... e altri {} endpoint'.format(len(paths) - 8))
except:
    print('    Errore nel parsing API')" 2>/dev/null || echo "    Errore nel recupero endpoint"
else
    echo "  ⚪ FastAPI non rilevato su porta 8000"
fi

# === 📝 CONFIGURAZIONE APPLICAZIONE ===
echo -e "\n📝 === CONFIGURAZIONE APPLICAZIONE ==="
echo "--- File .env ---"
if [ -f .env ]; then
    echo "  ✅ File .env trovato"
    echo "  Variabili configurate:"
    cat .env | grep -v "^#" | grep -v "^$" | sed 's/=.*/=***/' | sed 's/^/    /'
else
    echo "  ⚪ File .env non trovato"
fi

echo -e "\n--- Requirements/Dependencies ---"
if [ -f requirements.txt ]; then
    echo "  ✅ requirements.txt trovato ($(wc -l < requirements.txt) dipendenze)"
    echo "  Dipendenze principali:"
    head -10 requirements.txt | sed 's/^/    /'
elif [ -f pyproject.toml ]; then
    echo "  ✅ pyproject.toml trovato"
    echo "  Configurazione poetry/setuptools"
else
    echo "  ⚠️  Nessun file di dipendenze trovato"
fi

echo -e "\n--- Main application files ---"
find . -name "main.py" -o -name "app.py" -o -name "server.py" | head -3 | while read file; do
    echo "  📄 $file:"
    head -5 "$file" 2>/dev/null | grep -E "(import|from|def|class)" | head -3 | sed 's/^/    /'
done

# === 🔍 ANALISI CODICE ===
echo -e "\n🔍 === ANALISI CODICE ==="
echo "--- Framework utilizzati ---"
find . -name "*.py" -type f -exec grep -l "fastapi\|flask\|django" {} \; 2>/dev/null | head -3 | while read file; do
    framework=$(grep -E "(from fastapi|import fastapi|from flask|import flask|from django|import django)" "$file" | head -1 | awk '{print $2}' | cut -d'.' -f1)
    echo "  📄 $file: usa $framework"
done

echo -e "\n--- Database models ---"
find . -name "*.py" -type f | xargs grep -l "class.*Base\|declarative_base\|Model" 2>/dev/null | head -3 | while read file; do
    echo "  📄 $file:"
    grep "class.*:" "$file" | head -2 | sed 's/^/    /'
done

# === 🎯 URL E ACCESSI DI RETE ===
echo -e "\n🎯 === URL E ACCESSI DI RETE ==="
echo "--- URL per accesso locale (VM) ---"
echo "  Dashboard locale: http://127.0.0.1:8000/"
echo "  API docs locale: http://127.0.0.1:8000/docs"

echo -e "\n--- URL per accesso di rete (da altri dispositivi) ---"
echo "  Dashboard rete: http://$VM_IP:8000/"
echo "  API docs rete: http://$VM_IP:8000/docs"
echo "  Test API: curl http://$VM_IP:8000/api/stats"

echo -e "\n--- Test da dispositivi esterni ---"
echo "  Comando ping: ping $VM_IP"
echo "  Test porta web: telnet $VM_IP 8000"
echo "  Browser mobile: http://$VM_IP:8000/"

# === 📊 LOG E DEBUGGING ===
echo -e "\n📊 === LOG E DEBUGGING ==="
echo "--- Directory log ---"
if [ -d logs ]; then
    echo "  ✅ Directory logs/ trovata"
    ls -la logs/ | head -5 | sed 's/^/    /'
    
    echo "  Ultimi log entries:"
    find logs/ -name "*.log" -type f | head -1 | xargs tail -3 2>/dev/null | sed 's/^/    /' || echo "    Nessun log recente"
else
    echo "  ⚪ Directory logs/ non trovata"
fi

echo -e "\n--- Processi applicazione ---"
ps aux | grep -E "(python|uvicorn|gunicorn)" | grep -v grep | awk '{print "  " $11 " (PID:" $2 ", CPU:" $3 "%, MEM:" $4 "%)"}' || echo "  Nessun processo Python/web trovato"

# === 🔧 RACCOMANDAZIONI ===
echo -e "\n🔧 === RACCOMANDAZIONI SETUP ==="
echo "--- Firewall ---"
if ! command -v ufw >/dev/null 2>&1; then
    echo "  ⚠️  Considera di installare UFW: sudo apt install ufw"
fi

echo "--- Sicurezza di rete ---"
if netstat -tuln 2>/dev/null | grep -q ":8000.*0.0.0.0"; then
    echo "  ✅ Server configurato per accesso di rete (0.0.0.0:8000)"
else
    echo "  ⚠️  Server potrebbe essere limitato al localhost"
fi

echo "--- Performance ---"
available_ram=$(free | awk 'NR==2{print $7}')
if [ "$available_ram" -lt 512000 ]; then
    echo "  ⚠️  RAM disponibile bassa ($(free -h | awk 'NR==2{print $7}'))"
fi

# === 🎉 SUMMARY ===
echo -e "\n🎉 === SUMMARY CONFIGURAZIONE ==="
echo "  🌐 IP VM: $VM_IP"
echo "  🐍 Python: $(python --version 2>&1)"
echo "  🌐 Virtual env: $([ -n "$VIRTUAL_ENV" ] && echo "Attivo" || echo "Non attivo")"
echo "  🚀 API porta 8000: $(curl -s --max-time 2 http://127.0.0.1:8000/ >/dev/null 2>&1 && echo "OK" || echo "Non raggiungibile")"
echo "  🔥 Firewall: $(command -v ufw >/dev/null 2>&1 && echo "Installato" || echo "Non installato")"
echo "  🗄️  Database: $(pgrep postgres >/dev/null && echo "PostgreSQL attivo" || echo "PostgreSQL non rilevato")"

echo -e "\n🔗 QUICK ACCESS URLs:"
echo "  • Dashboard: http://$VM_IP:8000/dashboard"
echo "  • API Docs: http://$VM_IP:8000/docs"
echo "  • Network Test: curl http://$VM_IP:8000/api/stats"

echo -e "\n===================================================="
echo "✅ Analisi completata - $(date)"
echo "📄 Salva questo output per riferimenti futuri"
echo "===================================================="