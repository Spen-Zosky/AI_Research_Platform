import requests
import spacy
import sys
from collections import defaultdict

API_BASE_URL = "http://127.0.0.1:8000"

def get_source_content(source_id: int):
    # ... (logica invariata) ...
    try:
        response = requests.get(f"{API_BASE_URL}/projects/", params={"limit": 2000})
        response.raise_for_status()
        for project in response.json():
            for source in project.get('sources', []):
                if source['id'] == source_id: return source.get('content')
        return None
    except requests.exceptions.RequestException: return None

def save_entity_to_db(source_id: int, entity_text: str, entity_label: str):
    """Salva una singola entità nel database tramite API."""
    try:
        entity_data = {"text": entity_text, "label": entity_label}
        # Questo endpoint va ancora creato in app/main.py
        # Lo script non funzionerà finché non lo aggiungiamo
        print(f"  -> Salvo entità '{entity_text}' ({entity_label}) per fonte {source_id}...")
        # In una fase successiva, questo chiamerà l'API:
        # requests.post(f"{API_BASE_URL}/sources/{source_id}/entities", json=entity_data).raise_for_status()
    except Exception as e:
        print(f"   - ERRORE salvataggio: {e}")

def extract_and_save_entities(source_id: int, text: str):
    print("--- 2. Caricamento modello NLP e analisi... ---")
    if not text or not text.strip():
        print("Il contenuto della fonte è vuoto.")
        return

    nlp = spacy.load("it_core_news_lg")
    doc = nlp(text)
    
    found_entities = defaultdict(list)
    for ent in doc.ents:
        if ent.label_ in ["PER", "ORG", "GPE", "LOC"]:
            # Aggiunge solo se non è già presente per evitare duplicati
            if ent.text not in found_entities[ent.label_]:
                found_entities[ent.label_].append(ent.text)
    
    print("--- 3. Salvataggio Entità nel Database ---")
    if not found_entities:
        print("Nessuna entità rilevante trovata.")
        return

    # Aggiungeremo la logica per salvare nel DB nella prossima iterazione
    for label, items in found_entities.items():
        print(f"\n✅ Trovate {len(items)} entità di tipo '{label}':")
        for item in items:
            print(f"  - {item}")
            # Per ora, simuliamo il salvataggio
            # save_entity_to_db(source_id, item, label) 
    print("\nSimulazione di salvataggio completata. I dati verranno salvati nel DB nella prossima fase.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilizzo: python scripts/extract_entities.py <source_id>")
        sys.exit(1)
        
    source_id_to_process = int(sys.argv[1])
    content_to_analyze = get_source_content(source_id_to_process)
    
    if content_to_analyze:
        extract_and_save_entities(source_id_to_process, content_to_analyze)

