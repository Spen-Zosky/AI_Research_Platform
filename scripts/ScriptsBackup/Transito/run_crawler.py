import requests
from bs4 import BeautifulSoup
import sys
import os
import time

API_BASE_URL = "http://127.0.0.1:8000"

# --- Funzioni Helper ---

def get_all_projects():
    """Recupera tutti i progetti disponibili dalla nostra API."""
    try:
        response = requests.get(f"{API_BASE_URL}/projects/", params={"limit": 2000})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRORE: Impossibile recuperare la lista dei progetti: {e}")
        return None

def get_sources_for_project(project_id: int):
    """Recupera tutte le fonti per un dato progetto."""
    try:
        response = requests.get(f"{API_BASE_URL}/projects/{project_id}/sources/", params={"limit": 5000})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRORE: Impossibile recuperare le fonti per il progetto {project_id}: {e}")
        return []

def scrape_url_content(url: str):
    """Scarica una pagina web e ne estrae il testo pulito."""
    print(f"  -> Scraping di: {url[:70]}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')
        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return clean_text
    except requests.exceptions.RequestException as e:
        print(f"     ⚠️  ATTENZIONE: Impossibile fare lo scraping di {url}. Errore: {e}")
        return None

def save_content_to_db(source_id: int, content: str):
    """Salva il contenuto estratto nel database."""
    try:
        update_data = {"content": content}
        response = requests.put(f"{API_BASE_URL}/sources/{source_id}", json=update_data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"     ❌ ERRORE durante il salvataggio nel DB per la fonte {source_id}: {e}")
        return False

# --- Logica Principale del Crawler ---

if __name__ == "__main__":
    # Verifica che il server sia attivo
    try:
        requests.get(API_BASE_URL + "/docs", timeout=3)
    except requests.exceptions.ConnectionError:
        print("❌ ERRORE: Il server API non è in esecuzione.")
        print("Per favore, avvia il server in un altro terminale con: python -m app.main")
        sys.exit(1)

    # Mostra i progetti disponibili
    print("--- Progetti Disponibili per il Crawling ---")
    projects = get_all_projects()
    if not projects:
        sys.exit(1)
    
    for proj in projects:
        print(f"  ID: {proj['id']:<3} | Nome: {proj['name']}")
    
    try:
        project_id_choice = int(input("\nInserisci l'ID del progetto su cui eseguire il crawling: "))
    except ValueError:
        print("Scelta non valida. Uscita.")
        sys.exit(1)

    print(f"\n--- Inizio Crawling per il Progetto ID: {project_id_choice} ---")
    sources = get_sources_for_project(project_id_choice)
    
    if not sources:
        print("Nessuna fonte trovata per questo progetto.")
        sys.exit(0)

    total_sources = len(sources)
    processed_count = 0
    
    for i, source in enumerate(sources):
        print(f"\n[Processo {i+1}/{total_sources}] Fonte ID: {source['id']} - {source['title']}")
        
        # Controlla se la fonte ha già un contenuto
        if source.get('content'):
            print("  -> Contenuto già presente. Salto.")
            continue
            
        # Esegue lo scraping
        content = scrape_url_content(source['url'])
        
        if content:
            # Salva nel database
            if save_content_to_db(source['id'], content):
                processed_count += 1
                print(f"  -> ✅ Salvato con successo.")
        
        # Pausa di cortesia per non sovraccaricare il server di destinazione
        print("  -> Attendo 2 secondi...")
        time.sleep(2)

    print(f"\n--- ✅ Crawling Completato ---")
    print(f"Fonti processate e aggiornate in questa sessione: {processed_count}")
