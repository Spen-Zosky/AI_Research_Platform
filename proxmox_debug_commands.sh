# proxmox_debug_commands.sh
# Comandi per debug connettività da host Proxmox root

echo "🔍 PROXMOX DEBUG - AI RESEARCH PLATFORM"
echo "======================================="
echo "Host Proxmox: 192.168.1.10"
echo "VM Ubuntu: 192.168.1.20"
echo "Data: $(date)"
echo "======================================="

# === STATO VM ===
echo -e "\n🖥️ === STATO VM ==="
echo "--- Lista VM attive ---"
qm list | grep running | sed 's/^/  /'

echo -e "\n--- Stato VM 100 (Ubuntu) ---"
qm status 100 2>/dev/null && echo "  ✅ VM 100 in esecuzione" || echo "  ❌ VM 100 non trovata/spenta"

echo -e "\n--- Configurazione rete VM 100 ---"
qm config 100 | grep -E "(net|ip)" | sed 's/^/  /' 2>/dev/null || echo "  Impossibile leggere config VM 100"

# === TEST CONNETTIVITÀ PROXMOX → VM ===
echo -e "\n🌐 === TEST CONNETTIVITÀ PROXMOX → VM ==="
echo "--- Ping VM Ubuntu ---"
if ping -c 2 192.168.1.20 >/dev/null 2>&1; then
    echo "  ✅ Ping 192.168.1.20 OK"
    ping_time=$(ping -c 1 192.168.1.20 | grep "time=" | awk -F'time=' '{print $2}' | awk '{print $1}')
    echo "    Tempo risposta: ${ping_time}ms"
else
    echo "  ❌ Ping 192.168.1.20 FAIL"
fi

echo -e "\n--- Test porte VM Ubuntu ---"
for port in 22 8000 8001; do
    if timeout 3 bash -c "echo >/dev/tcp/192.168.1.20/$port" 2>/dev/null; then
        echo "  ✅ Porta $port aperta su 192.168.1.20"
    else
        echo "  ❌ Porta $port chiusa/filtrata su 192.168.1.20"
    fi
done

echo -e "\n--- Test HTTP API VM ---"
if curl -s --max-time 5 http://192.168.1.20:8000/ >/dev/null 2>&1; then
    echo "  ✅ API HTTP raggiungibile da Proxmox"
    
    # Test endpoint specifici
    for endpoint in "/docs" "/api/stats" "/dashboard"; do
        response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://192.168.1.20:8000$endpoint)
        echo "    $endpoint: HTTP $response_code"
    done
else
    echo "  ❌ API HTTP NON raggiungibile da Proxmox"
fi

# === FIREWALL PROXMOX ===
echo -e "\n🔥 === FIREWALL PROXMOX ==="
echo "--- Stato firewall datacenter ---"
if [ -f "/etc/pve/firewall/cluster.fw" ]; then
    echo "  ✅ Firewall cluster configurato"
    grep -E "^(ENABLE|POLICY)" /etc/pve/firewall/cluster.fw 2>/dev/null | sed 's/^/    /' || echo "    File vuoto o errore lettura"
else
    echo "  ⚪ Firewall cluster non configurato"
fi

echo -e "\n--- Firewall VM 100 ---"
if [ -f "/etc/pve/firewall/100.fw" ]; then
    echo "  ✅ Firewall VM 100 configurato"
    echo "    Regole attive:"
    grep -E "^(IN|OUT)" /etc/pve/firewall/100.fw 2>/dev/null | head -5 | sed 's/^/      /' || echo "      Nessuna regola trovata"
else
    echo "  ⚪ Firewall VM 100 non configurato (permesso tutto)"
fi

echo -e "\n--- iptables host Proxmox ---"
iptables -L INPUT | grep -E "(ACCEPT|DROP|REJECT)" | wc -l | awk '{print "  Regole iptables INPUT: " $1}'
iptables -L FORWARD | grep -E "(ACCEPT|DROP|REJECT)" | wc -l | awk '{print "  Regole iptables FORWARD: " $1}'

# === RETE LOCALE ===
echo -e "\n🏠 === TEST RETE LOCALE ==="
echo "--- Gateway e routing ---"
echo "  Gateway: $(ip route | grep default | awk '{print $3}')"
echo "  Rete locale: $(ip route | grep "192.168.1.0" | awk '{print $1}' | head -1)"

echo -e "\n--- Test connettività esterna ---"
ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "  ✅ Internet OK" || echo "  ❌ Problema internet"
ping -c 1 $(ip route | grep default | awk '{print $3}') >/dev/null 2>&1 && echo "  ✅ Gateway OK" || echo "  ❌ Gateway irraggiungibile"

echo -e "\n--- Scan rete locale (192.168.1.0/24) ---"
echo "  Dispositivi attivi nella rete:"
nmap -sn 192.168.1.0/24 2>/dev/null | grep -E "(Nmap scan report|MAC)" | head -10 | sed 's/^/    /' || echo "    nmap non disponibile"

# === BRIDGE E INTERFACCE ===
echo -e "\n🌉 === BRIDGE E INTERFACCE ==="
echo "--- Stato bridge vmbr0 ---"
ip link show vmbr0 | sed 's/^/  /'

echo -e "\n--- Interfacce collegate a vmbr0 ---"
bridge link show | grep vmbr0 | sed 's/^/  /' || echo "  Comando bridge non disponibile"

echo -e "\n--- Statistiche traffico vmbr0 ---"
cat /proc/net/dev | grep vmbr0 | awk '{print "  RX: " $2 " bytes, TX: " $10 " bytes"}' 2>/dev/null || echo "  Statistiche non disponibili"

# === MONITORAGGIO VM ===
echo -e "\n📊 === MONITORAGGIO VM ==="
echo "--- Risorse VM 100 ---"
if command -v qm >/dev/null 2>&1; then
    qm monitor 100 <<< "info status" 2>/dev/null | sed 's/^/  /' || echo "  Monitor non disponibile"
else
    echo "  Comando qm non trovato"
fi

echo -e "\n--- Processi VM correlati ---"
ps aux | grep -E "(kvm|qemu)" | grep "100" | head -3 | awk '{print "  " $11 " (PID:" $2 ")"}' || echo "  Nessun processo VM trovato"

# === TEST DA ALTRI CLIENT ===
echo -e "\n📱 === SIMULAZIONE TEST CLIENT ESTERNI ==="
echo "--- Comandi per test da altri dispositivi rete ---"
echo "  Windows:"
echo "    ping 192.168.1.20"
echo "    Test-NetConnection 192.168.1.20 -Port 8000"
echo "    Browser: http://192.168.1.20:8000/dashboard"

echo -e "\n  Linux/Mac:"
echo "    ping 192.168.1.20"
echo "    telnet 192.168.1.20 8000"
echo "    curl http://192.168.1.20:8000/api/stats"

echo -e "\n  Smartphone:"
echo "    Browser: http://192.168.1.20:8000/dashboard"

# === LOG E DEBUG ===
echo -e "\n📋 === LOG E DEBUG ==="
echo "--- Log sistema recenti (VM/rete) ---"
journalctl --since "10 minutes ago" | grep -E "(192.168.1.20|VM|qemu|kvm)" | tail -3 | sed 's/^/  /' || echo "  Nessun log recente"

echo -e "\n--- File configurazione Proxmox ---"
[ -f /etc/pve/qemu-server/100.conf ] && echo "  ✅ Config VM 100 presente" || echo "  ❌ Config VM 100 mancante"
[ -d /etc/pve/firewall ] && echo "  ✅ Directory firewall presente" || echo "  ⚪ Directory firewall assente"

# === RACCOMANDAZIONI ===
echo -e "\n💡 === RACCOMANDAZIONI PROXMOX ==="

# Check VM accessibility
if ! ping -c 1 192.168.1.20 >/dev/null 2>&1; then
    echo "  ⚠️  VM non raggiungibile - verifica:"
    echo "     1. VM accesa: qm start 100"
    echo "     2. Configurazione rete VM"
    echo "     3. Firewall Proxmox/VM"
fi

# Check API
if ! curl -s --max-time 3 http://192.168.1.20:8000/ >/dev/null 2>&1; then
    echo "  ⚠️  API non raggiungibile - verifica nella VM:"
    echo "     1. Server FastAPI avviato"
    echo "     2. Bind su 0.0.0.0:8000 (non 127.0.0.1)"
    echo "     3. Firewall Ubuntu (ufw status)"
fi

# Firewall check
if [ -f "/etc/pve/firewall/100.fw" ]; then
    if grep -q "ENABLE: 1" /etc/pve/firewall/100.fw 2>/dev/null; then
        echo "  ⚠️  Firewall VM attivo - verifica regole per porta 8000"
    fi
fi

echo -e "\n======================================"
echo "✅ Debug Proxmox completato"
echo "🖥️  Host: 192.168.1.10"
echo "🐧 VM: 192.168.1.20"
echo "🌐 Test: http://192.168.1.20:8000/dashboard"
echo "======================================"