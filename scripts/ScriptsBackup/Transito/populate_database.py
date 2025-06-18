import requests, os, sys, pandas as pd

API_BASE_URL = "http://127.0.0.1:8000"

def get_or_create_project(name: str, cache: dict):
    if name in cache: return cache[name]
    try:
        res = requests.post(f"{API_BASE_URL}/projects/", json={"name": name})
        if res.status_code == 422: # Already exists
            projects = requests.get(f"{API_BASE_URL}/projects/", params={"limit": 2000}).json()
            for p in projects:
                if p['name'] == name: cache[name] = p['id']; return p['id']
        res.raise_for_status()
        project_id = res.json()['id']
        cache[name] = project_id
        return project_id
    except Exception as e: return None

def import_file(path: str, cache: dict):
    if not os.path.exists(path): return 0
    print(f"\n-> Importo da '{path}'...")
    df = pd.read_excel(path)
    count = 0
    for _, row in df.iterrows():
        context, title, url = str(row.get("Contesto", "")), str(row.get("Nome", "")), str(row.get("URL", ""))
        if not all([context, title, url]): continue
        proj_id = get_or_create_project(context, cache)
        if proj_id:
            if not url.startswith('http'): url = f"https://{url}"
            try:
                requests.post(f"{API_BASE_URL}/projects/{proj_id}/sources/", json={"title": title, "url": url}).raise_for_status()
                count += 1
            except Exception: pass
    return count

if __name__ == "__main__":
    if input("Questo script CANCELLERA' il db e lo ripopolerà. Continuare? (s/n): ").lower() != 's': sys.exit("Annullato.")
    
    print("\n--- PASSO 1: Reset del Database ---")
    os.system("python init_db.py")
    
    print("\n--- PASSO 2: Importazione Dati ---")
    total = import_file("Sources_Dataset.xlsx", {})
    total += import_file("Harvesting_Dataset.xlsx", {})
    
    print(f"\n--- ✅ PROCESSO COMPLETATO. Fonti totali importate: {total} ---")
