#!/bin/bash
# start_network_server.sh - Avvia server per accesso di rete

echo "🌐 AVVIO AI RESEARCH PLATFORM PER RETE LOCALE"
echo "=============================================="
echo "📍 IP VM: 192.168.1.20"
echo "🔗 Dashboard: http://192.168.1.20:8000/dashboard"
echo "📚 API Docs: http://192.168.1.20:8000/docs"
echo "🌐 Network Info: http://192.168.1.20:8000/network-info"
echo "=============================================="

# Verifica virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔄 Attivazione virtual environment..."
    source venv/bin/activate
fi

# Installa dipendenze se necessario
echo "📦 Verifica dipendenze..."
pip install jinja2 python-multipart aiofiles pandas openpyxl --quiet

# Avvia server su tutte le interfacce di rete
echo "🚀 Avvio server FastAPI..."
echo "   Host: 0.0.0.0 (tutte le interfacce)"
echo "   Porta: 8000"
echo "   Reload: attivo"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "✅ Server terminato"
