# 🚀 Dashboard Sistema Web Scraping

Una dashboard web moderna e interattiva per gestire il sistema di web scraping e analisi contenuti.

## ✨ Caratteristiche

### 🎨 **Design Moderno**
- **Tema scuro** ispirato a GitHub
- **Layout responsive** con sidebar navigabile
- **Animazioni fluide** e feedback visivo
- **Icone intuitive** per ogni funzione

### 🛠️ **Funzionalità Complete**
- **Setup automatico** del sistema
- **Importazione dati** da Excel, CSV, Markdown
- **Web crawling** parallelo e sequenziale
- **Analisi NLP** con estrazione entità
- **Manutenzione sistema** e health checks
- **Monitoraggio real-time** con statistiche
- **Gestione database** completa

### 🔧 **Tecnologie**
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Backend**: FastAPI + Python
- **API**: RESTful con documentazione automatica
- **Real-time**: Log streaming e aggiornamenti stato

## 🚀 Avvio Rapido

### 1. **Installazione Dipendenze**
```bash
pip install fastapi uvicorn python-multipart
```

### 2. **Avvio Dashboard**
```bash
python run_dashboard.py
```

La dashboard si aprirà automaticamente nel browser all'indirizzo: `http://127.0.0.1:8001`

### 3. **Opzioni Avvio**
```bash
# Avvio con opzioni personalizzate
python run_dashboard.py --host 0.0.0.0 --port 8080

# Avvio senza aprire browser
python run_dashboard.py --no-browser

# Avvio in foreground (per debugging)
python run_dashboard.py --foreground

# Solo setup file (non avvia server)
python run_dashboard.py --setup-only
```

## 📱 Utilizzo Dashboard

### 🏠 **Dashboard Principale**
- **Statistiche sistema** aggiornate in tempo reale
- **Azioni rapide** per le operazioni più comuni
- **Stato API** e connessione database
- **Log sistema** con filtri per tipo

### 📥 **Sezione Importazione**
1. Clicca su "Importazione" nella sidebar
2. Scegli il tipo di file (Excel, CSV, Markdown)
3. Seleziona il file da importare
4. Monitora il progresso nei log

**Formati supportati:**
- **.xlsx/.xls**: File Excel con colonne Nome, URL, Contesto
- **.csv**: File CSV con separatori automatici
- **.md**: File Markdown con tabelle strutturate

### 🕷️ **Web Crawling**
1. Vai alla sezione "Web Crawling"
2. Seleziona il progetto da crawlare
3. Scegli modalità (Parallelo/Sequenziale)
4. Imposta numero di worker
5. Avvia il processo

**Modalità disponibili:**
- **Parallelo**: Più veloce, usa multiple connessioni
- **Sequenziale**: Più lento ma più sicuro

### 🧠 **Analisi NLP**
1. Accedi alla sezione "Analisi NLP"
2. Specifica una fonte (opzionale) o analizza tutto
3. Scegli tipo di analisi:
   - **Solo Entità**: Persone, organizzazioni, luoghi
   - **Solo Keywords**: Parole chiave importanti
   - **Entrambi**: Analisi completa
4. Avvia l'elaborazione

### 🗄️ **Gestione Database**
- **Inizializzazione**: Crea tabelle e struttura
- **Ottimizzazione**: Applica indici e performance tuning
- **Backup**: Salvataggio dati (pianificato)
- **Statistiche**: Visualizza metriche database

### 🔧 **Manutenzione Sistema**
- **Health Check**: Verifica stato componenti
- **Pulizia**: Rimuovi fonti problematiche
- **Report**: Genera report dettagliati
- **Ottimizzazione**: Migliora performance

## 🎛️ **Interfaccia**

### 📊 **Pannello Stato**
```
[🟢 Online]  Progetti: 15    Fonti: 1,247    Con Contenuto: 894
```

### 📋 **Log Real-time**
```
[12:34:56] ℹ️  Sistema dashboard avviato
[12:35:02] ✅ Crawling completato: 45 fonti processate
[12:35:15] ⚠️  Fonte ID 123 non raggiungibile
[12:35:30] 🧠 Analisi NLP: 156 entità estratte
```

### 🚀 **Azioni Rapide**
- **Setup Completo**: Inizializza tutto il sistema
- **Crawler Veloce**: Avvia crawling con impostazioni default
- **Analisi Express**: NLP su tutte le fonti senza contenuto
- **Health Check**: Verifica rapida dello stato

## 🔌 **API Endpoints**

La dashboard espone un'API RESTful completa:

### **Status e Monitoraggio**
- `GET /api/status` - Stato sistema
- `GET /api/health` - Health check
- `GET /api/logs` - Log sistema
- `GET /api/projects` - Lista progetti

### **Operazioni**
- `POST /api/setup/full` - Setup completo
- `POST /api/import/file` - Importa file
- `POST /api/crawler/run` - Avvia crawler
- `POST /api/nlp/analyze` - Analisi NLP
- `POST /api/maintenance/run` - Manutenzione

### **Database**
- `POST /api/database/init` - Inizializza DB
- `POST /api/database/optimize` - Ottimizza DB

### **Task Management**
- `GET /api/tasks/{task_id}` - Stato task
- `DELETE /api/tasks` - Pulisci task completati

### **Utilità**
- `GET /api/reports/generate` - Genera report
- `GET /api/export/data` - Esporta dati

**Documentazione completa**: `http://127.0.0.1:8001/docs`

## 🎯 **Esempi d'Uso**

### **Importazione Rapida**
```bash
curl -X POST "http://127.0.0.1:8001/api/import/file" \
     -F "file=@sources.xlsx" \
     -F "file_type=excel"
```

### **Crawling Automatico**
```bash
curl -X POST "http://127.0.0.1:8001/api/crawler/run" \
     -H "Content-Type: application/json" \
     -d '{"project_id": "all", "mode": "parallel", "max_workers": 5}'
```

### **Stato Sistema**
```bash
curl "http://127.0.0.1:8001/api/status"
```

## ⚙️ **Configurazione**

### **File di Configurazione**
La dashboard usa la configurazione del sistema principale:

```bash
# .env
API_BASE_URL=http://127.0.0.1:8000
DATABASE_URL=postgresql://user:pass@localhost/db
LOG_LEVEL=INFO
MAX_CRAWLER_WORKERS=3
```

### **Personalizzazione**
```python
# dashboard_config.py
DASHBOARD_CONFIG = {
    "theme": "dark",
    "auto_refresh": 30,  # secondi
    "max_log_entries": 100,
    "default_crawler_workers": 3
}
```

## 🛡️ **Sicurezza**

### **Accesso**
- Dashboard progettata per **uso locale**
- Per ambiente di produzione, implementare:
  - Autenticazione utenti
  - HTTPS/TLS
  - Rate limiting
  - Logging audit

### **CORS**
```python
# Per produzione, limitare origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🔧 **Troubleshooting**

### **Server Non Si Avvia**
```bash
# Verifica porta libera
netstat -an | grep 8001

# Prova porta diversa
python run_dashboard.py --port 8080
```

### **Dashboard Non Carica**
1. Verifica che `dashboard.html` esista
2. Controlla i log del server
3. Prova a ricreare i file: `python run_dashboard.py --setup-only`

### **API Non Risponde**
```bash
# Test connessione
curl http://127.0.0.1:8001/api/status

# Verifica log
tail -f logs/app.log
```

### **Operazioni Lente**
1. Riduci numero worker crawler
2. Ottimizza database: `POST /api/database/optimize`
3. Pulisci log e task: `DELETE /api/tasks`

## 📈 **Performance**

### **Ottimizzazioni**
- **Crawler parallelo**: Fino a 10 worker simultanei
- **Caching**: Progetti e statistiche in memoria
- **Batch processing**: Importazioni ottimizzate
- **Indici database**: Auto-applicati per PostgreSQL

### **Monitoraggio**
- **Metriche real-time**: Aggiornate ogni 30 secondi
- **Task tracking**: Stato di ogni operazione
- **Resource usage**: CPU e memoria tramite health checks

## 🚀 **Estensioni**

### **Aggiungere Nuove Funzioni**
1. Crea endpoint in `dashboard_server.py`
2. Aggiungi sezione in dashboard HTML
3. Implementa logica frontend
4. Aggiorna documentazione

### **Personalizzazione UI**
- Modifica CSS per temi personalizzati
- Aggiungi grafici con Chart.js
- Implementa notifiche desktop
- Integra WebSocket per real-time

### **Integrazioni**
- **Slack/Discord**: Notifiche automatiche
- **Email**: Report periodici
- **Webhook**: Eventi personalizzati
- **Monitoring**: Prometheus/Grafana

## 📞 **Supporto**

### **Log e Debug**
```bash
# Avvio con debug
python run_dashboard.py --foreground

# Log dettagliati
export LOG_LEVEL=DEBUG
python run_dashboard.py
```

### **Reset Completo**
```bash
# Rimuovi file generati
rm dashboard.html dashboard_server.py

# Ricrea tutto
python run_dashboard.py --setup-only
```

### **Info Sistema**
- **Python**: 3.8+
- **Memoria**: 512MB minimo
- **Disco**: 100MB per log e export
- **Rete**: Porta 8001 libera

---

## 🎉 **Conclusione**

La dashboard fornisce un'interfaccia completa e moderna per gestire il sistema di web scraping. Con il suo design intuitivo e le funzionalità avanzate, semplifica notevolmente la gestione quotidiana del sistema.

**Buon lavoro con la tua dashboard! 🚀**