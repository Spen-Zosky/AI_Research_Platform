# proxmox_firewall_config.sh
# Configurazione firewall Proxmox per permettere accesso alla VM

echo "🔥 CONFIGURAZIONE FIREWALL PROXMOX"
echo "=================================="
echo "VM Target: 192.168.1.20 (ID: 100)"
echo "Servizio: AI Research Platform (porta 8000)"
echo "=================================="

# === CONTROLLO STATO ATTUALE ===
echo -e "\n🔍 === STATO ATTUALE FIREWALL ==="

echo "--- Firewall Datacenter ---"
if [ -f "/etc/pve/firewall/cluster.fw" ]; then
    echo "  File cluster.fw presente"
    if grep -q "enable: 1" /etc/pve/firewall/cluster.fw 2>/dev/null; then
        echo "  ✅ Firewall datacenter ATTIVO"
    else
        echo "  ⚪ Firewall datacenter DISATTIVO"
    fi
else
    echo "  ⚪ File cluster.fw non presente"
fi

echo -e "\n--- Firewall VM 100 ---"
if [ -f "/etc/pve/firewall/100.fw" ]; then
    echo "  File 100.fw presente"
    if grep -q "enable: 1" /etc/pve/firewall/100.fw 2>/dev/null; then
        echo "  ✅ Firewall VM 100 ATTIVO"
        echo "  Regole attuali:"
        grep -E "^(IN|OUT)" /etc/pve/firewall/100.fw 2>/dev/null | sed 's/^/    /' || echo "    Nessuna regola custom"
    else
        echo "  ⚪ Firewall VM 100 DISATTIVO"
    fi
else
    echo "  ⚪ File 100.fw non presente (firewall disabilitato)"
fi

# === TEST CONNETTIVITÀ ===
echo -e "\n🌐 === TEST CONNETTIVITÀ ATTUALE ==="
echo "--- Ping VM ---"
ping -c 1 192.168.1.20 >/dev/null 2>&1 && echo "  ✅ Ping OK" || echo "  ❌ Ping FAIL"

echo -e "\n--- Test porte ---"
for port in 22 8000; do
    if timeout 2 bash -c "echo >/dev/tcp/192.168.1.20/$port" 2>/dev/null; then
        echo "  ✅ Porta $port: APERTA"
    else
        echo "  ❌ Porta $port: CHIUSA/FILTRATA"
    fi
done

# === FUNZIONI CONFIGURAZIONE ===

create_vm_firewall_config() {
    echo -e "\n🔧 === CREAZIONE CONFIGURAZIONE FIREWALL VM ==="
    
    # Crea configurazione firewall per VM 100
    cat > /etc/pve/firewall/100.fw << 'EOF'
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT

[RULES]
# SSH access
IN SSH(ACCEPT) -i net0
# HTTP/HTTPS access
IN HTTP(ACCEPT) -i net0
IN HTTPS(ACCEPT) -i net0
# Custom FastAPI port 8000
IN ACCEPT -i net0 -source 192.168.1.0/24 -dport 8000 -proto tcp
# Allow all from local network (alternative)
#IN ACCEPT -i net0 -source 192.168.1.0/24
EOF

    echo "  ✅ Configurazione firewall VM creata"
    echo "  📄 File: /etc/pve/firewall/100.fw"
}

create_datacenter_firewall_config() {
    echo -e "\n🔧 === CONFIGURAZIONE FIREWALL DATACENTER ==="
    
    # Backup del file esistente se presente
    if [ -f "/etc/pve/firewall/cluster.fw" ]; then
        cp /etc/pve/firewall/cluster.fw /etc/pve/firewall/cluster.fw.backup
        echo "  ✅ Backup creato: cluster.fw.backup"
    fi
    
    # Configurazione permissiva per rete locale
    cat > /etc/pve/firewall/cluster.fw << 'EOF'
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT

[RULES]
# Allow local network traffic
IN ACCEPT -source 192.168.1.0/24
# SSH from local network
IN SSH(ACCEPT) -source 192.168.1.0/24
# Web interfaces from local network
IN HTTP(ACCEPT) -source 192.168.1.0/24
IN HTTPS(ACCEPT) -source 192.168.1.0/24
# Proxmox web interface
IN ACCEPT -source 192.168.1.0/24 -dport 8006 -proto tcp
EOF

    echo "  ✅ Configurazione firewall datacenter creata"
    echo "  📄 File: /etc/pve/firewall/cluster.fw"
}

disable_firewall() {
    echo -e "\n🔓 === DISABILITAZIONE FIREWALL (per debug) ==="
    
    # Disabilita firewall VM
    if [ -f "/etc/pve/firewall/100.fw" ]; then
        sed -i 's/enable: 1/enable: 0/' /etc/pve/firewall/100.fw
        echo "  ✅ Firewall VM 100 disabilitato"
    fi
    
    # Disabilita firewall datacenter
    if [ -f "/etc/pve/firewall/cluster.fw" ]; then
        sed -i 's/enable: 1/enable: 0/' /etc/pve/firewall/cluster.fw
        echo "  ✅ Firewall datacenter disabilitato"
    fi
    
    echo "  ⚠️  ATTENZIONE: Firewall completamente disabilitato per debug"
    echo "     Riabilitare dopo aver risolto i problemi"
}

test_after_config() {
    echo -e "\n🧪 === TEST DOPO CONFIGURAZIONE ==="
    
    echo "Attesa 5 secondi per applicazione regole..."
    sleep 5
    
    echo -e "\n--- Test connettività ---"
    ping -c 1 192.168.1.20 >/dev/null 2>&1 && echo "  ✅ Ping: OK" || echo "  ❌ Ping: FAIL"
    timeout 3 bash -c "echo >/dev/tcp/192.168.1.20/22" 2>/dev/null && echo "  ✅ SSH (22): OK" || echo "  ❌ SSH (22): FAIL"
    timeout 3 bash -c "echo >/dev/tcp/192.168.1.20/8000" 2>/dev/null && echo "  ✅ API (8000): OK" || echo "  ❌ API (8000): FAIL"
    
    echo -e "\n--- Test API HTTP ---"
    if curl -s --max-time 3 http://192.168.1.20:8000/ >/dev/null 2>&1; then
        echo "  ✅ API HTTP risponde"
    else
        echo "  ❌ API HTTP non risponde"
    fi
}

# === MENU INTERATTIVO ===
show_firewall_menu() {
    echo -e "\n🔥 MENU CONFIGURAZIONE FIREWALL:"
    echo "1. 📊 Stato attuale firewall"
    echo "2. 🔧 Crea config firewall VM (permissivo per rete locale)"
    echo "3. 🏢 Crea config firewall datacenter"
    echo "4. 🔓 Disabilita firewall (debug)"
    echo "5. 🧪 Test dopo configurazione"
    echo "6. 📋 Mostra configurazioni"
    echo "7. ❌ Esci"
    echo -e "\nScegli opzione (1-7):"
}

show_configs() {
    echo -e "\n📋 === CONFIGURAZIONI ATTUALI ==="
    
    echo "--- VM 100 Firewall ---"
    if [ -f "/etc/pve/firewall/100.fw" ]; then
        cat /etc/pve/firewall/100.fw | sed 's/^/  /'
    else
        echo "  File non presente"
    fi
    
    echo -e "\n--- Datacenter Firewall ---"
    if [ -f "/etc/pve/firewall/cluster.fw" ]; then
        cat /etc/pve/firewall/cluster.fw | sed 's/^/  /'
    else
        echo "  File non presente"
    fi
}

# === MAIN EXECUTION ===
if [ "$1" = "auto" ]; then
    echo "🚀 CONFIGURAZIONE AUTOMATICA"
    create_vm_firewall_config
    test_after_config
    echo -e "\n✅ Configurazione automatica completata"
    echo "🌐 Test da client: http://192.168.1.20:8000/dashboard"
    exit 0
fi

# Menu interattivo
while true; do
    show_firewall_menu
    read -r choice
    
    case $choice in
        1) echo "Stato già mostrato sopra" ;;
        2) create_vm_firewall_config ;;
        3) create_datacenter_firewall_config ;;
        4) disable_firewall ;;
        5) test_after_config ;;
        6) show_configs ;;
        7) echo "👋 Uscita"; exit 0 ;;
        *) echo "❌ Opzione non valida" ;;
    esac
    
    echo -e "\nPremi ENTER per continuare..."
    read -r
done

# === COMANDI RAPIDI ===
echo -e "\n💡 === COMANDI RAPIDI ==="
echo "# Configurazione automatica (permissiva per rete locale):"
echo "bash $0 auto"
echo ""
echo "# Disabilita tutto (per debug):"
echo "echo 'enable: 0' > /etc/pve/firewall/100.fw"
echo "echo 'enable: 0' > /etc/pve/firewall/cluster.fw"
echo ""
echo "# Test manuale:"
echo "ping 192.168.1.20"
echo "curl http://192.168.1.20:8000/api/stats"