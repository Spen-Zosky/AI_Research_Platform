import requests
from bs4 import BeautifulSoup
import sys
import os

API_BASE_URL = "http://127.0.0.1:8000"

def get_source_url(source_id: int):
    # Logica per ottenere l'URL... (invariata)
    # ...
    # Questa parte rimane la stessa
    try:
        response = requests.get(f"{API_BASE_URL}/projects/", params={"limit": 2000})
        response.raise_for_status()
        projects = response.json()
        for project in projects:
            for source in project.get('sources', []):
                if source['id'] == source_id:
                    print(f"✅ URL trovato: {source['url']}")
                    return source['url']
        return None
    except requests.exceptions.RequestException:
        return None

def scrape_url_content(url: str):
    # Logica di scraping... (invariata)
    # ...
    # Questa parte rimane la stessa
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        return clean_text
    except requests.exceptions.RequestException:
        return None

def save_content_to_db(source_id: int, content: str):
    """Salva il contenuto estratto nel database tramite una chiamata API PUT."""
    print(f"--- 3. Salvataggio del contenuto nel DB per la Fonte ID: {source_id} ---")
    try:
        update_data = {"content": content}
        response = requests.put(f"{API_BASE_URL}/sources/{source_id}", json=update_data)
        response.raise_for_status()
        print(f"✅ Contenuto salvato con successo nel database.")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRORE durante il salvataggio nel database: {e}")
        if e.response:
            print("Dettagli errore:", e.response.text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilizzo: python scripts/scrape_single_source.py <source_id>")
        sys.exit(1)
    
    source_id_to_scrape = int(sys.argv[1])
    
    url_to_scrape = get_source_url(source_id_to_scrape)
    if not url_to_scrape:
        print(f"Impossibile trovare l'URL per la fonte ID {source_id_to_scrape}")
        sys.exit(1)
        
    print(f"Inizio scraping per URL: {url_to_scrape}")
    scraped_content = scrape_url_content(url_to_scrape)
    
    if scraped_content:
        print(f"Testo estratto con successo ({len(scraped_content)} caratteri).")
        save_content_to_db(source_id_to_scrape, scraped_content)
    else:
        print("Nessun contenuto estratto.")
