import requests
import os
import sys
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000"

def get_or_create_project(project_name: str, project_cache: dict):
    """
    Ottiene l'ID di un progetto dalla cache o lo crea se non esiste.
    Questo ottimizza l'operazione, evitando chiamate API superflue.
    """
    if project_name in project_cache:
        return project_cache[project_name]
    
    print(f"\n[API] Verifica/Creazione del progetto: '{project_name}'...")
    try:
        # Prima cerchiamo se il progetto esiste già
        response = requests.get(f"{API_BASE_URL}/projects/", params={"limit": 2000})
        response.raise_for_status()
        projects = response.json()
        for p in projects:
            if p['name'] == project_name:
                project_cache[project_name] = p['id']
                print(f"  -> Progetto esistente trovato con ID: {p['id']}")
                return p['id']
        
        # Se non esiste, lo creiamo
        project_data = {"name": project_name, "description": f"Progetto per le fonti del contesto '{project_name}'."}
        response = requests.post(f"{API_BASE_URL}/projects/", json=project_data)
        response.raise_for_status()
        project = response.json()
        project_id = project['id']
        project_cache[project_name] = project_id
        print(f"  -> Nuovo progetto creato con ID: {project_id}")
        return project_id
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRORE CRITICO durante la gestione del progetto '{project_name}': {e}")
        return None

def import_data(file_path: str):
    """
    Funzione principale per importare dati da un file Excel (.xlsx) in modo additivo.
    """
    if not os.path.exists(file_path):
        print(f"❌ ERRORE: Il file '{file_path}' non è stato trovato.")
        return
        
    print(f"\n--- 🚀 Inizio Importazione Dati da '{file_path}' ---")
    
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ ERRORE: Impossibile leggere il file Excel. Dettagli: {e}")
        return

    project_cache = {}
    total_imported = 0
    total_skipped = 0

    # Itera su ogni riga del DataFrame
    for index, row in df.iterrows():
        context_name = row.get("Contesto")
        title = row.get("Nome")
        url = row.get("URL")

        if pd.isna(context_name) or pd.isna(title) or pd.isna(url):
            total_skipped += 1
            continue

        project_id = get_or_create_project(context_name, project_cache)

        if project_id:
            if not str(url).startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            source_data = {"title": str(title), "url": str(url)}
            try:
                requests.post(
                    f"{API_BASE_URL}/projects/{project_id}/sources/",
                    json=source_data
                ).raise_for_status()
                total_imported += 1
                if total_imported % 100 == 0:
                    print(f"  -> Fonti importate in questa sessione: {total_imported}...")
            except requests.exceptions.RequestException as e:
                # Gestisce il caso in cui una fonte esista già (conflitto)
                if e.response and e.response.status_code == 500: # O 409, a seconda dell'implementazione API
                     total_skipped +=1
                else:
                    print(f"⚠️  ATTENZIONE: Impossibile importare '{title}'. Errore: {e.response.text if e.response else e}")
                    total_skipped += 1

    print(f"\n--- ✅ Importazione Completata per il file '{file_path}' ---")
    print(f"Fonti aggiunte con successo in questa sessione: {total_imported}")
    print(f"Righe scartate (dati mancanti o errori): {total_skipped}")

if __name__ == "__main__":
    # Verifica che il server sia attivo
    try:
        requests.get(API_BASE_URL + "/docs", timeout=3)
    except requests.exceptions.ConnectionError:
        print("❌ ERRORE: Il server API non è in esecuzione.")
        print("Per favore, avvia il server in un altro terminale con: python -m app.main")
        sys.exit(1)

    # Elenca i file disponibili e chiede all'utente di scegliere
    print("File di dati disponibili per l'importazione:")
    print("1: Sources_Dataset.xlsx (Fonti Documentali)")
    print("2: Harvesting_Dataset.xlsx (Fonti per Data Harvesting)")
    choice = input("Quale file vuoi importare? (1/2): ")

    if choice == '1':
        file_to_import = "Sources_Dataset.xlsx"
    elif choice == '2':
        file_to_import = "Harvesting_Dataset.xlsx"
    else:
        print("Scelta non valida. Uscita.")
        sys.exit(1)

    import_data(file_to_import)
