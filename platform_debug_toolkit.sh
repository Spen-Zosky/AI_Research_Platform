#!/bin/bash
# platform_debug_toolkit.sh
# Toolkit completo per debug e troubleshooting

VM_IP=$(ip route get 8.8.8.8 | awk '{print $7; exit}')

echo "🛠️ PLATFORM DEBUG TOOLKIT"
echo "========================="
echo "IP VM: $VM_IP"
echo "Data: $(date)"
echo "========================="

# === MENU INTERATTIVO ===
show_menu() {
    echo -e "\n🔧 OPZIONI DEBUG:"
    echo "1. 🔍 Analisi completa piattaforma"
    echo "2. 🌐 Test connettività di rete"
    echo "3. 🚀 Verifica server FastAPI"
    echo "4. 🗄️ Controllo database"
    echo "5. 🔥 Diagnostica firewall"
    echo "6. 📊 Monitor in tempo reale"
    echo "7. 🔧 Fix automatico problemi comuni"
    echo "8. 📄 Genera report completo"
    echo "9. ❌ Esci"
    echo -e "\nScegli opzione (1-9):"
}

# === FUNZIONI DEBUG ===

debug_platform_analysis() {
    echo -e "\n🔍 === ANALISI COMPLETA PIATTAFORMA ==="
    
    # Verifica directory progetto
    if [ ! -f "app/main.py" ]; then
        echo "❌ ERRORE: Non siamo nella directory del progetto"
        echo "💡 Vai nella directory: cd ~/AI_Research_Platform"
        return 1
    fi
    
    echo "✅ Directory progetto OK"
    
    # Verifica virtual environment
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "⚠️ Virtual environment NON attivo"
        echo "💡 Attiva con: source venv/bin/activate"
    else
        echo "✅ Virtual environment attivo: $VIRTUAL_ENV"
    fi
    
    # Verifica dipendenze
    echo -e "\n--- Dipendenze critiche ---"
    critical_deps=("fastapi" "uvicorn" "sqlalchemy" "psycopg2" "jinja2")
    for dep in "${critical_deps[@]}"; do
        if pip show "$dep" >/dev/null 2>&1; then
            version=$(pip show "$dep" | grep Version | cut -d' ' -f2)
            echo "  ✅ $dep: $version"
        else
            echo "  ❌ $dep: NON INSTALLATO"
        fi
    done
    
    # Verifica file configurazione
    echo -e "\n--- File configurazione ---"
    if [ -f ".env" ]; then
        echo "  ✅ .env presente"
        if grep -q "DATABASE_URL" .env; then
            echo "    ✅ DATABASE_URL configurato"
        else
            echo "    ⚠️ DATABASE_URL mancante"
        fi
    else
        echo "  ❌ .env mancante"
    fi
    
    # Verifica template frontend
    if [ -d "app/templates" ]; then
        echo "  ✅ Directory templates presente"
        template_count=$(find app/templates -name "*.html" | wc -l)
        echo "    📄 Template HTML: $template_count"
    else
        echo "  ⚠️ Directory templates mancante"
    fi
}

debug_network_connectivity() {
    echo -e "\n🌐 === TEST CONNETTIVITÀ DI RETE ==="
    
    echo "--- Test porte locali ---"
    for port in 8000 8001 8080; do
        if lsof -Pi :$port -sTCP:LISTEN >/dev/null 2>&1; then
            process=$(lsof -Pi :$port -sTCP:LISTEN | tail -1 | awk '{print $1 " (PID:" $2 ")"}')
            echo "  ✅ Porta $port: $process"
        else
            echo "  ❌ Porta $port: libera"
        fi
    done
    
    echo -e "\n--- Test bind address ---"
    if netstat -tuln 2>/dev/null | grep ":8000" | grep -q "0.0.0.0"; then
        echo "  ✅ Server bind su 0.0.0.0 (accesso rete OK)"
    elif netstat -tuln 2>/dev/null | grep ":8000" | grep -q "127.0.0.1"; then
        echo "  ⚠️ Server bind su 127.0.0.1 (solo localhost)"
        echo "    💡 Riavvia con: uvicorn app.main:app --host 0.0.0.0 --port 8000"
    else
        echo "  ❌ Server non in ascolto su porta 8000"
    fi
    
    echo -e "\n--- Test connettività esterna ---"
    if timeout 3 bash -c "echo >/dev/tcp/$VM_IP/8000" 2>/dev/null; then
        echo "  ✅ Porta 8000 raggiungibile da $VM_IP"
    else
        echo "  ❌ Porta 8000 NON raggiungibile da $VM_IP"
    fi
    
    echo -e "\n--- Test HTTP response ---"
    for url in "http://127.0.0.1:8000" "http://$VM_IP:8000"; do
        if curl -s --max-time 3 "$url/" >/dev/null 2>&1; then
            echo "  ✅ $url - OK"
        else
            echo "  ❌ $url - FAIL"
        fi
    done
}

debug_fastapi_server() {
    echo -e "\n🚀 === VERIFICA SERVER FASTAPI ==="
    
    # Processo uvicorn
    uvicorn_process=$(ps aux | grep uvicorn | grep -v grep)
    if [ -n "$uvicorn_process" ]; then
        echo "✅ Processo uvicorn trovato:"
        echo "$uvicorn_process" | sed 's/^/  /'
    else
        echo "❌ Processo uvicorn NON trovato"
        echo "💡 Avvia con: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
        return 1
    fi
    
    # Test endpoint API
    echo -e "\n--- Test endpoint API ---"
    endpoints=("/" "/docs" "/openapi.json")
    for endpoint in "${endpoints[@]}"; do
        response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://127.0.0.1:8000$endpoint")
        if [ "$response_code" = "200" ]; then
            echo "  ✅ $endpoint - HTTP 200"
        else
            echo "  ❌ $endpoint - HTTP $response_code"
        fi
    done
    
    # Test API specifica piattaforma
    if curl -s --max-time 3 "http://127.0.0.1:8000/api/stats" >/dev/null 2>&1; then
        echo "  ✅ API custom endpoint funzionante"
    else
        echo "  ⚠️ API custom endpoint non implementato"
    fi
    
    # Verifica log errori
    echo -e "\n--- Log errori recenti ---"
    if [ -f "logs/app.log" ]; then
        echo "Ultimi errori:"
        tail -10 logs/app.log | grep -i error | tail -3 | sed 's/^/  /'
    else
        echo "File log non trovato"
    fi
}

debug_database() {
    echo -e "\n🗄️ === CONTROLLO DATABASE ==="
    
    # PostgreSQL process
    if pgrep postgres >/dev/null; then
        echo "✅ PostgreSQL in esecuzione"
        
        # Test connessione
        if python3 -c "
import sys
sys.path.append('.')
try:
    from app.core.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version()'))
        print('✅ Connessione database OK')
    print('✅ Database raggiungibile')
except Exception as e:
    print(f'❌ Errore database: {e}')
" 2>/dev/null; then
            echo "✅ Test connessione database OK"
        else
            echo "❌ Errore connessione database"
        fi
        
        # Verifica tabelle
        echo -e "\n--- Tabelle database ---"
        python3 -c "
import sys
sys.path.append('.')
try:
    from app.core.database import engine
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f'Tabelle trovate: {len(tables)}')
    for table in tables:
        print(f'  ✅ {table}')
except Exception as e:
    print(f'❌ Errore: {e}')
" 2>/dev/null
    else
        echo "❌ PostgreSQL NON in esecuzione"
        echo "💡 Avvia con: sudo systemctl start postgresql"
    fi
}

debug_firewall() {
    echo -e "\n🔥 === DIAGNOSTICA FIREWALL ==="
    
    # UFW status
    if command -v ufw >/dev/null 2>&1; then
        ufw_status=$(sudo ufw status 2>/dev/null)
        echo "--- UFW Status ---"
        echo "$ufw_status" | sed 's/^/  /'
        
        if echo "$ufw_status" | grep -q "Status: active"; then
            if echo "$ufw_status" | grep -q "8000"; then
                echo "✅ Regola per porta 8000 presente"
            else
                echo "⚠️ Porta 8000 non aperta nel firewall"
                echo "💡 Comando: sudo ufw allow 8000/tcp"
            fi
        fi
    else
        echo "UFW non installato"
    fi
    
    # iptables check
    echo -e "\n--- iptables Rules ---"
    if sudo iptables -L INPUT 2>/dev/null | grep -q "8000\|ACCEPT.*tcp.*dpt:8000"; then
        echo "✅ Regole iptables per porta 8000 trovate"
    else
        echo "⚪ Nessuna regola iptables specifica per porta 8000"
    fi
}

monitor_realtime() {
    echo -e "\n📊 === MONITOR TEMPO REALE ==="
    echo "Premi Ctrl+C per uscire"
    echo "=========================="
    
    while true; do
        clear
        echo "🔄 MONITOR TEMPO REALE - $(date)"
        echo "IP VM: $VM_IP"
        echo "================================"
        
        # CPU e RAM
        echo "💻 SISTEMA:"
        echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')"
        echo "  RAM: $(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
        
        # Processi web
        echo -e "\n🚀 PROCESSI WEB:"
        ps aux | grep -E "(uvicorn|python|fastapi)" | grep -v grep | head -3 | awk '{print "  " $11 " (CPU:" $3 "%)"}' || echo "  Nessun processo trovato"
        
        # Connessioni rete
        echo -e "\n🌐 CONNESSIONI ATTIVE:"
        netstat -an 2>/dev/null | grep ":8000" | wc -l | awk '{print "  Connessioni porta 8000: " $1}'
        
        # Test API veloce
        echo -e "\n🔍 TEST API:"
        if curl -s --max-time 1 "http://127.0.0.1:8000/" >/dev/null 2>&1; then
            echo "  ✅ API localhost OK"
        else
            echo "  ❌ API localhost FAIL"
        fi
        
        if curl -s --max-time 1 "http://$VM_IP:8000/" >/dev/null 2>&1; then
            echo "  ✅ API rete OK"
        else
            echo "  ❌ API rete FAIL"
        fi
        
        sleep 2
    done
}

auto_fix_common_issues() {
    echo -e "\n🔧 === FIX AUTOMATICO PROBLEMI COMUNI ==="
    
    # 1. Virtual environment
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "⚠️ Virtual environment non attivo"
        echo "💡 Attivalo manualmente: source venv/bin/activate"
    fi
    
    # 2. Dipendenze mancanti
    echo -e "\n--- Installazione dipendenze mancanti ---"
    missing_deps=()
    for dep in "fastapi" "uvicorn" "jinja2" "python-multipart"; do
        if ! pip show "$dep" >/dev/null 2>&1; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo "Installazione dipendenze: ${missing_deps[*]}"
        pip install "${missing_deps[@]}"
    else
        echo "✅ Tutte le dipendenze sono installate"
    fi
    
    # 3. Directory mancanti
    echo -e "\n--- Creazione directory mancanti ---"
    for dir in "app/templates" "app/static" "logs"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo "✅ Creata directory: $dir"
        fi
    done
    
    # 4. Firewall
    echo -e "\n--- Configurazione firewall ---"
    if command -v ufw >/dev/null 2>&1; then
        if sudo ufw status | grep -q "Status: active" && ! sudo ufw status | grep -q "8000"; then
            echo "Apertura porta 8000 nel firewall..."
            sudo ufw allow 8000/tcp
            echo "✅ Porta 8000 aperta"
        fi
    fi
    
    echo -e "\n✅ Fix automatico completato"
}

generate_full_report() {
    echo -e "\n📄 === GENERAZIONE REPORT COMPLETO ==="
    
    report_file="platform_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "🚀 AI RESEARCH PLATFORM - REPORT COMPLETO"
        echo "=========================================="
        echo "Data: $(date)"
        echo "IP VM: $VM_IP"
        echo "Host: $(hostname)"
        echo "User: $(whoami)"
        echo "Directory: $(pwd)"
        echo "=========================================="
        
        debug_platform_analysis
        debug_network_connectivity
        debug_fastapi_server
        debug_database
        debug_firewall
        
        echo -e "\n🎯 === SUMMARY ==="
        echo "Report generato automaticamente"
        echo "File: $report_file"
        echo "=========================================="
        
    } > "$report_file"
    
    echo "✅ Report salvato in: $report_file"
    echo "📄 Dimensione: $(du -h "$report_file" | cut -f1)"
}

# === MAIN LOOP ===
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1) debug_platform_analysis ;;
        2) debug_network_connectivity ;;
        3) debug_fastapi_server ;;
        4) debug_database ;;
        5) debug_firewall ;;
        6) monitor_realtime ;;
        7) auto_fix_common_issues ;;
        8) generate_full_report ;;
        9) echo "👋 Arrivederci!"; exit 0 ;;
        *) echo "❌ Opzione non valida" ;;
    esac
    
    echo -e "\nPremi ENTER per continuare..."
    read -r
done