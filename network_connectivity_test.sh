#!/bin/bash
# network_connectivity_test.sh
# Test completo connettività per piattaforma su VM Proxmox

VM_IP=$(ip route get 8.8.8.8 | awk '{print $7; exit}')

echo "🌐 TEST CONNETTIVITÀ DI RETE - AI RESEARCH PLATFORM"
echo "=================================================="
echo "IP VM: $VM_IP"
echo "Data: $(date)"
echo "=================================================="

# === TEST CONNETTIVITÀ LOCALE ===
echo -e "\n🔍 === TEST CONNETTIVITÀ LOCALE ==="

echo "--- Test localhost ---"
for port in 8000 8001 8080; do
    if curl -s --max-time 3 http://127.0.0.1:$port/ >/dev/null 2>&1; then
        echo "  ✅ localhost:$port - OK"
    else
        echo "  ❌ localhost:$port - FAIL"
    fi
done

echo -e "\n--- Test processo in ascolto ---"
for port in 8000 8001 8080; do
    if lsof -Pi :$port -sTCP:LISTEN >/dev/null 2>&1; then
        process=$(lsof -Pi :$port -sTCP:LISTEN | tail -1 | awk '{print $1}')
        echo "  ✅ Porta $port: $process in ascolto"
    else
        echo "  ❌ Porta $port: nessun processo in ascolto"
    fi
done

# === TEST ACCESSIBILITÀ DI RETE ===
echo -e "\n🌐 === TEST ACCESSIBILITÀ DI RETE ==="

echo "--- Test bind address ---"
for port in 8000 8001 8080; do
    bind_info=$(netstat -tuln 2>/dev/null | grep ":$port " || ss -tuln | grep ":$port ")
    if echo "$bind_info" | grep -q "0.0.0.0:$port"; then
        echo "  ✅ Porta $port: bind su 0.0.0.0 (accesso di rete OK)"
    elif echo "$bind_info" | grep -q "127.0.0.1:$port"; then
        echo "  ⚠️  Porta $port: bind su 127.0.0.1 (solo localhost)"
    elif echo "$bind_info" | grep -q ":$port"; then
        echo "  ✅ Porta $port: bind su tutte le interfacce"
    else
        echo "  ❌ Porta $port: non in ascolto"
    fi
done

echo -e "\n--- Test connessione da IP VM ---"
for port in 8000 8001 8080; do
    if timeout 3 bash -c "echo >/dev/tcp/$VM_IP/$port" 2>/dev/null; then
        echo "  ✅ $VM_IP:$port - CONNESSIONE OK"
        
        # Test HTTP specifico
        if [ $port -eq 8000 ]; then
            if curl -s --max-time 3 http://$VM_IP:$port/ >/dev/null 2>&1; then
                echo "    ✅ HTTP response OK"
            else
                echo "    ⚠️  Porta aperta ma HTTP non risponde"
            fi
        fi
    else
        echo "  ❌ $VM_IP:$port - CONNESSIONE FALLITA"
    fi
done

# === TEST API ENDPOINTS ===
echo -e "\n🚀 === TEST API ENDPOINTS ==="

if curl -s --max-time 5 http://$VM_IP:8000/ >/dev/null 2>&1; then
    echo "  ✅ API base endpoint raggiungibile"
    
    # Test endpoint specifici
    endpoints=("/docs" "/openapi.json" "/api/stats" "/dashboard")
    for endpoint in "${endpoints[@]}"; do
        response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://$VM_IP:8000$endpoint)
        if [ "$response_code" = "200" ]; then
            echo "    ✅ $endpoint - HTTP 200 OK"
        elif [ "$response_code" = "404" ]; then
            echo "    ⚠️  $endpoint - HTTP 404 (endpoint non implementato)"
        elif [ "$response_code" = "000" ]; then
            echo "    ❌ $endpoint - Timeout/connessione fallita"
        else
            echo "    ⚠️  $endpoint - HTTP $response_code"
        fi
    done
    
    # Test JSON response
    if curl -s --max-time 3 http://$VM_IP:8000/api/stats | python3 -m json.tool >/dev/null 2>&1; then
        echo "    ✅ API JSON response valida"
    else
        echo "    ⚠️  API JSON response non valida o endpoint inesistente"
    fi
else
    echo "  ❌ API non raggiungibile da IP di rete"
fi

# === TEST FIREWALL ===
echo -e "\n🔥 === TEST FIREWALL ====="

echo "--- Stato UFW ---"
if command -v ufw >/dev/null 2>&1; then
    ufw_status=$(sudo ufw status 2>/dev/null)
    if echo "$ufw_status" | grep -q "Status: active"; then
        echo "  ✅ UFW attivo"
        if echo "$ufw_status" | grep -q "8000"; then
            echo "    ✅ Regola per porta 8000 trovata"
        else
            echo "    ⚠️  Nessuna regola per porta 8000"
            echo "    💡 Suggerimento: sudo ufw allow 8000/tcp"
        fi
    else
        echo "  ⚪ UFW inattivo"
    fi
else
    echo "  ⚪ UFW non installato"
fi

echo -e "\n--- iptables (regole attive) ---"
if sudo iptables -L INPUT 2>/dev/null | grep -q "8000"; then
    echo "  ✅ Regole iptables per porta 8000 trovate"
else
    echo "  ⚪ Nessuna regola iptables specifica per porta 8000"
fi

# === TEST DA PROSPETTIVA CLIENT ===
echo -e "\n📱 === SIMULAZIONE CLIENT ESTERNI ==="

echo "--- Comandi di test per client Windows ---"
echo "  ping $VM_IP"
echo "  Test-NetConnection $VM_IP -Port 8000"
echo "  Invoke-WebRequest http://$VM_IP:8000/api/stats"
echo "  Browser: http://$VM_IP:8000/dashboard"

echo -e "\n--- Comandi di test per client Linux/Mac ---"
echo "  ping $VM_IP"
echo "  telnet $VM_IP 8000"
echo "  curl http://$VM_IP:8000/api/stats"
echo "  Browser: http://$VM_IP:8000/dashboard"

echo -e "\n--- Test da smartphone/tablet ---"
echo "  Browser mobile: http://$VM_IP:8000/dashboard"
echo "  (Assicurati che il dispositivo sia nella stessa rete)"

# === DIAGNOSTICA AVANZATA ===
echo -e "\n🔧 === DIAGNOSTICA AVANZATA ==="

echo "--- Interfacce di rete ---"
ip_info=$(ip addr show | grep -E "(inet |UP|DOWN)")
echo "$ip_info" | sed 's/^/  /'

echo -e "\n--- Routing table ---"
ip route | sed 's/^/  /'

echo -e "\n--- Connessioni attive ---"
netstat -an 2>/dev/null | grep ":8000" | sed 's/^/  /' || ss -an | grep ":8000" | sed 's/^/  /'

echo -e "\n--- Test DNS resolution ---"
if nslookup google.com >/dev/null 2>&1; then
    echo "  ✅ DNS resolution OK"
else
    echo "  ⚠️  Problemi DNS"
fi

# === RACCOMANDAZIONI ===
echo -e "\n💡 === RACCOMANDAZIONI ==="

# Check bind address
if netstat -tuln 2>/dev/null | grep ":8000" | grep -q "127.0.0.1"; then
    echo "  ⚠️  Server FastAPI bind su localhost - configurare per 0.0.0.0"
    echo "     Comando: uvicorn app.main:app --host 0.0.0.0 --port 8000"
fi

# Check firewall
if command -v ufw >/dev/null 2>&1 && sudo ufw status 2>/dev/null | grep -q "Status: active" && ! sudo ufw status | grep -q "8000"; then
    echo "  ⚠️  Firewall attivo ma porta 8000 non aperta"
    echo "     Comando: sudo ufw allow 8000/tcp"
fi

# Check if API is responding
if ! curl -s --max-time 3 http://$VM_IP:8000/ >/dev/null 2>&1; then
    echo "  ⚠️  API non risponde da IP di rete"
    echo "     1. Verifica che il server sia avviato"
    echo "     2. Controlla bind address (deve essere 0.0.0.0)"
    echo "     3. Verifica firewall"
fi

# === SUMMARY E NEXT STEPS ===
echo -e "\n🎯 === SUMMARY CONNETTIVITÀ ==="

# Calcola score di connettività
score=0
total_tests=4

# Test 1: Processo in ascolto
lsof -Pi :8000 -sTCP:LISTEN >/dev/null 2>&1 && score=$((score + 1))

# Test 2: Bind corretto
(netstat -tuln 2>/dev/null | grep ":8000" | grep -q "0.0.0.0" || ss -tuln | grep ":8000" | grep -q "0.0.0.0") && score=$((score + 1))

# Test 3: Connessione da IP VM
timeout 3 bash -c "echo >/dev/tcp/$VM_IP/8000" 2>/dev/null && score=$((score + 1))

# Test 4: HTTP response
curl -s --max-time 3 http://$VM_IP:8000/ >/dev/null 2>&1 && score=$((score + 1))

echo "  Connettività Score: $score/$total_tests"

if [ $score -eq $total_tests ]; then
    echo "  🎉 CONNETTIVITÀ PERFETTA - Piattaforma accessibile da rete"
    echo "  🔗 URL principale: http://$VM_IP:8000/dashboard"
elif [ $score -ge 2 ]; then
    echo "  ⚠️  CONNETTIVITÀ PARZIALE - Alcuni problemi da risolvere"
else
    echo "  ❌ PROBLEMI CONNETTIVITÀ - Configurazione necessaria"
fi

echo -e "\n🚀 === NEXT STEPS ==="
if [ $score -lt $total_tests ]; then
    echo "  1. Esegui setup frontend con configurazione di rete"
    echo "  2. Configura server FastAPI per 0.0.0.0:8000"
    echo "  3. Apri porta 8000 nel firewall"
    echo "  4. Testa da dispositivo esterno"
else
    echo "  ✅ Configurazione ottimale!"
    echo "  🔗 Testa da altri dispositivi: http://$VM_IP:8000/dashboard"
fi

echo -e "\n=================================================="
echo "✅ Test connettività completato - $(date)"
echo "📄 IP VM: $VM_IP"
echo "🌐 URL di test: http://$VM_IP:8000/"
echo "=================================================="