# one_command_analysis.sh
# Comando singolo per analisi completa - copia e incolla nel terminale

{
echo "🚀 ANALISI RAPIDA AI RESEARCH PLATFORM"
echo "======================================"
echo "Data: $(date)"
VM_IP=$(ip route get 8.8.8.8 | awk '{print $7; exit}')
echo "IP VM: $VM_IP"
echo "======================================"

echo -e "\n🌐 RETE:"
echo "  Gateway: $(ip route | grep default | awk '{print $3}')"
echo "  DNS: $(grep nameserver /etc/resolv.conf | head -1 | awk '{print $2}')"
ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "  Internet: ✅ OK" || echo "  Internet: ❌ FAIL"

echo -e "\n🔥 FIREWALL:"
if command -v ufw >/dev/null 2>&1; then
    ufw_status=$(sudo ufw status 2>/dev/null | head -1)
    echo "  UFW: $ufw_status"
    sudo ufw status 2>/dev/null | grep -q "8000" && echo "  Porta 8000: ✅ APERTA" || echo "  Porta 8000: ⚠️ NON CONFIGURATA"
else
    echo "  UFW: Non installato"
fi

echo -e "\n🐍 PYTHON:"
echo "  Versione: $(python --version 2>&1)"
[ -n "$VIRTUAL_ENV" ] && echo "  Venv: ✅ ATTIVO ($VIRTUAL_ENV)" || echo "  Venv: ❌ NON ATTIVO"
[ -f requirements.txt ] && echo "  Requirements: ✅ PRESENTE" || echo "  Requirements: ⚠️ MANCANTE"

echo -e "\n🗄️ DATABASE:"
pgrep postgres >/dev/null && echo "  PostgreSQL: ✅ ATTIVO" || echo "  PostgreSQL: ❌ NON ATTIVO"

echo -e "\n🚀 SERVER:"
lsof -Pi :8000 -sTCP:LISTEN >/dev/null 2>&1 && echo "  Porta 8000: ✅ IN ASCOLTO" || echo "  Porta 8000: ❌ LIBERA"
if netstat -tuln 2>/dev/null | grep ":8000" | grep -q "0.0.0.0"; then
    echo "  Bind: ✅ 0.0.0.0 (rete OK)"
elif netstat -tuln 2>/dev/null | grep ":8000" | grep -q "127.0.0.1"; then
    echo "  Bind: ⚠️ 127.0.0.1 (solo localhost)"
else
    echo "  Bind: ❌ NON RILEVATO"
fi

echo -e "\n🔍 TEST API:"
curl -s --max-time 3 http://127.0.0.1:8000/ >/dev/null 2>&1 && echo "  Localhost: ✅ OK" || echo "  Localhost: ❌ FAIL"
curl -s --max-time 3 http://$VM_IP:8000/ >/dev/null 2>&1 && echo "  Rete ($VM_IP): ✅ OK" || echo "  Rete ($VM_IP): ❌ FAIL"

echo -e "\n📁 STRUTTURA:"
[ -f app/main.py ] && echo "  app/main.py: ✅ PRESENTE" || echo "  app/main.py: ❌ MANCANTE"
[ -d app/templates ] && echo "  templates: ✅ PRESENTE" || echo "  templates: ❌ MANCANTE"
[ -f .env ] && echo "  .env: ✅ PRESENTE" || echo "  .env: ❌ MANCANTE"

echo -e "\n📊 DIPENDENZE:"
for dep in fastapi uvicorn sqlalchemy psycopg2; do
    pip show "$dep" >/dev/null 2>&1 && echo "  $dep: ✅" || echo "  $dep: ❌"
done

echo -e "\n🎯 QUICK URLS:"
echo "  Dashboard: http://$VM_IP:8000/dashboard"
echo "  API Docs: http://$VM_IP:8000/docs"
echo "  Test API: curl http://$VM_IP:8000/api/stats"

echo -e "\n📱 TEST DA ALTRI DISPOSITIVI:"
echo "  Windows: Test-NetConnection $VM_IP -Port 8000"
echo "  Linux/Mac: telnet $VM_IP 8000"
echo "  Browser: http://$VM_IP:8000/dashboard"

echo -e "\n💡 COMANDI UTILI:"
[ -z "$VIRTUAL_ENV" ] && echo "  Attiva venv: source venv/bin/activate"
! lsof -Pi :8000 -sTCP:LISTEN >/dev/null 2>&1 && echo "  Avvia server: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
netstat -tuln 2>/dev/null | grep ":8000" | grep -q "127.0.0.1" && echo "  Fix rete: uvicorn app.main:app --host 0.0.0.0 --port 8000"
command -v ufw >/dev/null 2>&1 && ! sudo ufw status 2>/dev/null | grep -q "8000" && echo "  Apri firewall: sudo ufw allow 8000/tcp"

echo -e "\n======================================"
echo "✅ Analisi completata - $(date)"
echo "📋 IP VM: $VM_IP"
echo "======================================"
}