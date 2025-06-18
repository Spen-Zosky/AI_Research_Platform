# 🌐 AI Research Platform - Accesso di Rete

## 📍 Configurazione VM Proxmox
- **IP Virtual Machine**: `192.168.1.20`
- **Porta Server**: `8000`
- **Protocollo**: HTTP
- **Accesso**: Rete locale completa

## 🔗 URL di Accesso

### 🖥️ Interfacce Web Principali
```
Dashboard:     http://192.168.1.20:8000/dashboard
Progetti:      http://192.168.1.20:8000/projects/view
Ricerca:       http://192.168.1.20:8000/search/view
Importazione:  http://192.168.1.20:8000/import
API Docs:      http://192.168.1.20:8000/docs
Network Info:  http://192.168.1.20:8000/network-info
```

### 🔌 Endpoint API
```
Base URL:      http://192.168.1.20:8000
Statistiche:   http://192.168.1.20:8000/api/stats
Ricerca:       http://192.168.1.20:8000/search/?q=termine
Progetti:      http://192.168.1.20:8000/projects/
```

## 📱 Test di Connettività

### Da Computer nella Rete
```bash
# Test ping
ping 192.168.1.20

# Test porta HTTP
telnet 192.168.1.20 8000
# oppure
nc -zv 192.168.1.20 8000

# Test API
curl http://192.168.1.20:8000/api/stats
```

### Da Browser
1. **Desktop/Laptop**: http://192.168.1.20:8000/dashboard
2. **Smartphone**: http://192.168.1.20:8000/dashboard
3. **Tablet**: http://192.168.1.20:8000/dashboard

## 🚀 Avvio del Server

### Metodo 1: Script Automatico
```bash
./start_network_server.sh
```

### Metodo 2: Comando Manuale
```bash
# Attiva virtual environment
source venv/bin/activate

# Avvia server per rete
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 Risoluzione Problemi

### Se non raggiungibile dalla rete:

1. **Verifica IP VM**
   ```bash
   ip addr show
   hostname -I
   ```

2. **Controlla Firewall**
   ```bash
   sudo ufw status
   sudo ufw allow 8000/tcp
   ```

3. **Verifica Processo Server**
   ```bash
   ps aux | grep uvicorn
   netstat -tuln | grep 8000
   ```

4. **Test Locale**
   ```bash
   curl http://localhost:8000/api/stats
   curl http://127.0.0.1:8000/api/stats
   ```

### Se il frontend non carica:
- Controlla che i template esistano in `app/templates/`
- Verifica che le dipendenze siano installate: `pip install jinja2 python-multipart`
- Guarda i log del server per errori

## 🔒 Sicurezza Rete Locale

**✅ Configurazione Attuale**: Sicura per rete locale privata

**⚠️ Per Accesso Internet**: Implementare:
- HTTPS/SSL con certificati
- Autenticazione utenti
- Firewall con whitelist IP
- Rate limiting e protezione DDoS
- VPN per accesso remoto sicuro

## 📊 Monitoraggio

### Log del Server
```bash
# Visualizza log in tempo reale
tail -f logs/app.log
```

### Statistiche Sistema
```bash
# API per statistiche
curl http://192.168.1.20:8000/api/stats | python -m json.tool
```

### Controllo Risorse
```bash
# Uso CPU/RAM
htop
# Connessioni di rete
netstat -an | grep 8000
```

---

**🎉 La piattaforma è ora accessibile da tutta la rete locale!**

Generato il: 2025-06-18 16:02:22
