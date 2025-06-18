# =================================================================
# CONFIGURAZIONE SISTEMA DI WEB SCRAPING E ANALISI CONTENUTI
# =================================================================
# 
# ISTRUZIONI:
# 1. Copia questo file in .env
# 2. Modifica i valori secondo la tua configurazione
# 3. NON committare il file .env su repository pubblici
#

# =================================================================
# DATABASE CONFIGURATION
# =================================================================

# URL di connessione al database PostgreSQL
# Formato: postgresql://username:password@host:port/database_name
DATABASE_URL=postgresql://user:password@localhost:5432/scraping_db

# Configurazione pool di connessioni database
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30

# =================================================================
# API CONFIGURATION
# =================================================================

# URL base dell'API del sistema
API_BASE_URL=http://127.0.0.1:8000

# Timeout per le richieste API (secondi)
API_TIMEOUT=30

# Numero massimo di retry per richieste API fallite
API_MAX_RETRIES=3

# =================================================================
# WEB SCRAPING CONFIGURATION
# =================================================================

# Timeout per le richieste di scraping (secondi)
SCRAPING_TIMEOUT=15

# Numero di tentativi di retry per scraping fallito
SCRAPING_RETRY_ATTEMPTS=3

# Delay tra i retry di scraping (secondi)
SCRAPING_RETRY_DELAY=2.0

# Delay tra richieste per rate limiting (secondi)
SCRAPING_RATE_LIMIT=2.0

# Dimensione massima del contenuto da scaricare (bytes)
SCRAPING_MAX_CONTENT_LENGTH=5000000

# User-Agent per le richieste web
SCRAPING_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36

# =================================================================
# LOGGING CONFIGURATION
# =================================================================

# Livello di logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Percorso del file di log (opzionale, se vuoto logga solo su console)
LOG_FILE_PATH=logs/app.log

# Formato dei messaggi di log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# =================================================================
# NATURAL LANGUAGE PROCESSING
# =================================================================

# Modello spaCy per l'italiano (deve essere installato)
SPACY_MODEL=it_core_news_lg

# Numero massimo di parole chiave da estrarre per documento
MAX_KEYWORDS=20

# Soglia minima di confidenza per le entità estratte
ENTITY_CONFIDENCE_THRESHOLD=0.5

# =================================================================
# PARALLEL PROCESSING
# =================================================================

# Numero massimo di worker per il crawling parallelo
MAX_CRAWLER_WORKERS=3

# Numero massimo di worker per l'elaborazione parallela
MAX_PROCESSING_WORKERS=2

# =================================================================
# SYSTEM MAINTENANCE
# =================================================================

# Numero di giorni per cui mantenere i log statistici
STATS_RETENTION_DAYS=30

# Soglia di utilizzo disco per warning (percentuale)
DISK_WARNING_THRESHOLD=80

# Soglia di utilizzo disco per errore critico (percentuale)
DISK_CRITICAL_THRESHOLD=90

# =================================================================
# EXTERNAL SERVICES (opzionali)
# =================================================================

# Configurazioni per servizi esterni come Redis, Elasticsearch, etc.
# REDIS_URL=redis://localhost:6379/0
# ELASTICSEARCH_URL=http://localhost:9200

# =================================================================
# SECURITY
# =================================================================

# Secret key per la generazione di token (se implementata autenticazione)
# SECRET_KEY=your-secret-key-here

# Lista di domini consentiti per CORS (separati da virgola)
# ALLOWED_HOSTS=localhost,127.0.0.1

# =================================================================
# DEVELOPMENT/PRODUCTION FLAGS
# =================================================================

# Ambiente di esecuzione (development, production, testing)
ENVIRONMENT=development

# Abilita mode debug (true/false)
DEBUG=false

# Abilita profiling delle performance (true/false)
ENABLE_PROFILING=false

# =================================================================
# EXAMPLE VALUES
# =================================================================
# 
# Esempio di configurazione per ambiente di sviluppo locale:
#
# DATABASE_URL=postgresql://postgres:password@localhost:5432/scraping_dev
# API_BASE_URL=http://localhost:8000
# LOG_LEVEL=DEBUG
# LOG_FILE_PATH=logs/dev.log
# MAX_CRAWLER_WORKERS=2
# ENVIRONMENT=development
# DEBUG=true
#
# =================================================================
# 
# Esempio di configurazione per ambiente di produzione:
#
# DATABASE_URL=postgresql://prod_user:secure_password@db.example.com:5432/scraping_prod
# API_BASE_URL=https://api.example.com
# LOG_LEVEL=INFO
# LOG_FILE_PATH=/var/log/scraping/app.log
# MAX_CRAWLER_WORKERS=5
# SCRAPING_RATE_LIMIT=1.0
# ENVIRONMENT=production
# DEBUG=false
#
# =================================================================
