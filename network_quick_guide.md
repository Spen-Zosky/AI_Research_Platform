# 🌐 Setup Rete per VM Proxmox - Guida Rapida

## ⚡ Configurazione in 5 Minuti

### **Passo 1: Trova IP della VM**
```bash
# Nella VM, trova l'IP
ip addr show | grep "inet " | grep -v "127.0.0.1"
# oppure
hostname -I
```

Esempio output: `192.168.1.150` (questo sarà il tuo IP)

### **Passo 2: Salva lo Script di Setup**
```bash
# Crea il file
nano setup_frontend_network.py

# Copia tutto il contenuto dello script "network_frontend_setup"
# Salva con Ctrl+X, Y, Enter
```

### **Passo 3: Esegui Setup Automatico**
```bash
# Assicurati che il virtual environment sia attivo
source venv/bin/activate

# Esegui setup completo
python setup_frontend_network.py
```

Lo script:
- ✅ Rileva automaticamente l'IP della VM
- ✅ Installa tutte le dipendenze necessarie
- ✅ Configura FastAPI per accesso di rete
- ✅ Crea template HTML ottimizzati
- ✅ Configura CORS per tutti i client
- ✅ Apre la porta 8000 nel firewall
- ✅ Crea script di avvio automatico

### **Passo 4: Avvia il Server**
```bash
# Usa lo script creato automaticamente
./start_network_server.sh

# OPPURE comando manuale
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Passo 5: Testa l'Accesso**

**Da qualsiasi dispositivo nella rete:**

1. **Browser**: `http://192.168.1.150:8000/dashboard` (sostituisci con il TUO IP)
2. **Ping test**: `ping 192.168.1.150`
3. **API test**: `curl http://192.168.1.150:8000/api/stats`

---

## 🎯 **URL Completi di Accesso**

Sostituisci `192.168.1.150` con l'IP della TUA VM:

### 🖥️ **Interfacce Web**
- **Dashboard Principale**: `http://192.168.1.150:8000/dashboard`
- **Gestione Progetti**: `http://192.168.1.150:8000/projects/view`
- **Ricerca Contenuti**: `http://192.168.1.150:8000/search/view`
- **Importazione Dati**: `http://192.168.1.150:8000/import`
- **API Documentation**: `http://192.168.1.150:8000/docs`
- **Info di Rete**: `http://192.168.1.150:8000/network-info`

### 🔌 **API Endpoints**
- **Statistiche Sistema**: `http://192.168.1.150:8000/api/stats`
- **Ricerca Full-text**: `http://192.168.1.150:8000/search/?q=termine`
- **Lista Progetti**: `http://192.168.1.150:8000/projects/`

---

## 📱 **Test da Diversi Dispositivi**

### **Computer Windows**
```cmd
# Ping test
ping 192.168.1.150

# Browser
start http://192.168.1.150:8000/dashboard

# PowerShell API test
Invoke-WebRequest http://192.168.1.150:8000/api/stats
```

### **Computer Mac/Linux**
```bash
# Ping test
ping 192.168.1.150

# Browser
open http://192.168.1.150:8000/dashboard  # Mac
xdg-open http://192.168.1.150:8000/dashboard  # Linux

# API test
curl http://192.168.1.150:8000/api/stats | python -m json.tool
```

### **Smartphone/Tablet**
- Apri il browser
- Vai su: `http://192.168.1.150:8000/dashboard`
- L'interfaccia è responsive e funziona su mobile

### **Altri Computer della Rete**
- Qualsiasi browser su: `http://192.168.1.150:8000/dashboard`
- Le funzionalità sono identiche a quelle locali

---

## 🔧 **Risoluzione Problemi Rapida**

### ❌ **"Sito non raggiungibile"**
```bash
# 1. Verifica IP VM
ip addr show

# 2. Verifica server in esecuzione
ps aux | grep uvicorn

# 3. Verifica porta aperta
sudo netstat -tuln | grep 8000

# 4. Controlla firewall
sudo ufw status
sudo ufw allow 8000/tcp  # Se necessario
```

### ❌ **"Connessione rifiutata"**
```bash
# Riavvia server con configurazione di rete
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### ❌ **"Pagina bianca o errori"**
```bash
# Verifica dipendenze
pip install jinja2 python-multipart aiofiles pandas openpyxl

# Controlla log errori nel terminale del server
```

### ❌ **"CORS Error" nel browser**
- Lo script configura automaticamente CORS
- Se persiste, riavvia il server

---

## 🚀 **Funzionalità Complete Disponibili**

Una volta configurato, da **QUALSIASI dispositivo** nella rete puoi:

### 📊 **Dashboard**
- Visualizzare statistiche in tempo reale
- Monitorare progetti e fonti
- Accesso a tutte le funzionalità

### 📁 **Gestione Progetti**
- Creare nuovi progetti
- Visualizzare progetti esistenti
- Gestire fonti per progetto

### 🔍 **Ricerca Avanzata**
- Ricerca full-text in tutti i contenuti
- Risultati istantanei
- Navigazione intuitiva

### 📥 **Importazione Dati**
- Upload file Excel/CSV da qualsiasi dispositivo
- Mapping automatico delle colonne
- Feedback in tempo reale

### 📚 **API Completa**
- Documentazione Swagger interattiva
- Tutti gli endpoint funzionanti
- Accesso programmatico da altri sistemi

---

## 🔐 **Sicurezza Rete Locale**

### ✅ **Configurazione Sicura per Rete Privata**
- Accesso limitato alla rete locale
- CORS configurato per la tua rete
- Firewall aperto solo per porta necessaria

### ⚠️ **NON Esporre su Internet**
Questa configurazione è **solo per rete locale**. Per accesso internet:
- Configura HTTPS con certificati SSL
- Implementa autenticazione utenti
- Usa VPN per accesso remoto sicuro
- Configura rate limiting e protezione DDoS

---

## 📈 **Prestazioni Ottimali**

### **Connessioni Simultanee**
- Il server gestisce multiple connessioni
- Ogni dispositivo può accedere simultaneamente
- No interferenze tra utenti diversi

### **Aggiornamenti Real-time**
- Le statistiche si aggiornano automaticamente
- Cambiamenti visibili su tutti i dispositivi
- Sincronizzazione automatica

---

## 🎉 **Risultato Finale**

Dopo il setup avrai:

🌐 **Accesso Universale**: Tutti i dispositivi della rete possono usare la piattaforma

📱 **Multi-device**: Computer, smartphone, tablet - tutto funziona

🔄 **Sincronizzato**: Dati sempre aggiornati su tutti i dispositivi

⚡ **Veloce**: Accesso LAN ad alta velocità

🛡️ **Sicuro**: Limitato alla tua rete privata

📊 **Completo**: Tutte le funzionalità disponibili ovunque

---

## 📞 **Supporto**

### **Informazioni Sistema**
```bash
# IP della VM
hostname -I

# Stato server
ps aux | grep uvicorn

# Log in tempo reale
tail -f logs/app.log

# Test API locale
curl http://localhost:8000/api/stats
```

### **File Utili Creati**
- `start_network_server.sh` - Script di avvio
- `NETWORK_SETUP_INFO.md` - Documentazione completa
- `app/main.py.network_backup` - Backup del file originale

---

🎯 **In 5 minuti hai trasformato la tua VM Proxmox in una piattaforma accessibile da tutta la rete!**

**Tutti i dispositivi possono ora accedere alla dashboard su:**
# 🌐 `http://[IP_TUA_VM]:8000/dashboard`