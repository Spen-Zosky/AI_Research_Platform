# improved_extract_entities.py
import sys
import logging
from typing import Dict, List, Optional, Set
from collections import defaultdict, Counter
import spacy
from spacy.lang.it.stop_words import STOP_WORDS
from utils import api_client, retry_on_failure, progress_tracker
from config import config

logger = logging.getLogger(__name__)

class EntityExtractor:
    """Estrattore avanzato di entità named entity recognition"""
    
    def __init__(self):
        self.api = api_client
        self.nlp = None
        self._load_nlp_model()
        
        # Configurazione per tipi di entità da estrarre
        self.entity_types = {
            "PERSON": ["PER"],  # Persone
            "ORGANIZATION": ["ORG"],  # Organizzazioni
            "LOCATION": ["GPE", "LOC"],  # Luoghi geografici
            "MISC": ["MISC"]  # Varie
        }
        
        # Parole da filtrare (oltre agli stop words)
        self.filter_words = STOP_WORDS.union({
            'essere', 'avere', 'fare', 'dire', 'andare', 'potere', 'dovere',
            'volere', 'sapere', 'dare', 'stare', 'vedere', 'uscire', 'venire'
        })
    
    def _load_nlp_model(self):
        """Carica il modello spaCy per l'italiano"""
        try:
            logger.info("Caricamento modello NLP italiano...")
            self.nlp = spacy.load("it_core_news_lg")
            logger.info("Modello NLP caricato con successo")
        except OSError:
            logger.error("Modello it_core_news_lg non trovato. Installa con: python -m spacy download it_core_news_lg")
            raise
    
    @retry_on_failure(max_attempts=3, delay=2.0)
    def get_source_content(self, source_id: int) -> Optional[Dict]:
        """Recupera il contenuto di una fonte"""
        logger.info(f"Recupero contenuto per fonte ID: {source_id}")
        
        projects = self.api.get("/projects/", params={"limit": 2000})
        if not projects:
            return None
        
        for project in projects:
            for source in project.get('sources', []):
                if source['id'] == source_id:
                    return source
        
        logger.error(f"Fonte {source_id} non trovata")
        return None
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """Estrae entità dal testo usando spaCy"""
        if not text or not text.strip():
            logger.warning("Testo vuoto fornito per l'estrazione di entità")
            return {}
        
        logger.info(f"Estrazione entità da testo di {len(text)} caratteri")
        
        # Processa il testo con spaCy
        doc = self.nlp(text)
        
        # Raggruppa entità per tipo
        entities_by_type = defaultdict(list)
        entity_counts = defaultdict(Counter)
        
        for ent in doc.ents:
            # Filtra entità troppo corte o comuni
            if len(ent.text.strip()) < 2:
                continue
            
            if ent.text.lower() in self.filter_words:
                continue
            
            # Mappa il tipo di entità spaCy ai nostri tipi
            mapped_type = None
            for our_type, spacy_types in self.entity_types.items():
                if ent.label_ in spacy_types:
                    mapped_type = our_type
                    break
            
            if mapped_type:
                entity_text = ent.text.strip()
                entity_counts[mapped_type][entity_text] += 1
        
        # Converti in formato finale, mantenendo solo entità con frequenza > 1 o molto importanti
        final_entities = {}
        for entity_type, counter in entity_counts.items():
            entities_list = []
            for text, count in counter.most_common():
                # Mantieni entità che appaiono più volte o sono lunghe (probabilmente importanti)
                if count > 1 or len(text) > 10:
                    entities_list.append({
                        "text": text,
                        "frequency": count,
                        "confidence": min(count / 10.0, 1.0)  # Confidence basata sulla frequenza
                    })
            
            if entities_list:
                final_entities[entity_type] = entities_list
        
        return final_entities
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[Dict]:
        """Estrae parole chiave dal testo"""
        if not text:
            return []
        
        doc = self.nlp(text)
        
        # Estrae token significativi
        keywords = []
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and 
                len(token.text) > 3 and
                token.pos_ in ['NOUN', 'ADJ', 'VERB']):
                keywords.append(token.lemma_.lower())
        
        # Conta frequenze
        keyword_counts = Counter(keywords)
        
        # Ritorna i più frequenti
        result = []
        for keyword, count in keyword_counts.most_common(max_keywords):
            result.append({
                "text": keyword,
                "frequency": count,
                "type": "KEYWORD"
            })
        
        return result
    
    @retry_on_failure(max_attempts=3, delay=1.0)
    def save_entities(self, source_id: int, entities: Dict[str, List[Dict]], keywords: List[Dict]) -> bool:
        """Salva entità e parole chiave nel database"""
        logger.info(f"Salvataggio entità per fonte {source_id}")
        
        try:
            # Prepara i dati per il database
            all_entities = []
            
            # Aggiungi entità named
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    all_entities.append({
                        "text": entity["text"],
                        "label": entity_type,
                        "frequency": entity["frequency"],
                        "confidence": entity["confidence"]
                    })
            
            # Aggiungi keywords
            for keyword in keywords:
                all_entities.append({
                    "text": keyword["text"],
                    "label": "KEYWORD",
                    "frequency": keyword["frequency"],
                    "confidence": 0.8  # Confidence fissa per keywords
                })
            
            if not all_entities:
                logger.info("Nessuna entità da salvare")
                return True
            
            # Salva tramite API
            # NOTA: Questo endpoint deve essere implementato nell'API
            # POST /sources/{source_id}/entities
            for entity in all_entities:
                result = self.api.post(f"/sources/{source_id}/entities", json=entity)
                if result is None:
                    logger.warning(f"Errore nel salvare entità: {entity['text']}")
            
            logger.info(f"Salvate {len(all_entities)} entità per fonte {source_id}")
            return True
            
        except Exception as e:
            logger.error(f"Errore nel salvare entità: {e}")
            return False
    
    def process_source(self, source_id: int) -> bool:
        """Processa una singola fonte per l'estrazione di entità"""
        try:
            # 1. Recupera il contenuto
            source_info = self.get_source_content(source_id)
            if not source_info:
                return False
            
            content = source_info.get('content', '')
            if not content or not content.strip():
                logger.warning(f"Nessun contenuto trovato per fonte {source_id}")
                return False
            
            logger.info(f"Processamento fonte {source_id}: {source_info.get('title', 'N/A')}")
            
            # 2. Estrae entità
            entities = self.extract_entities(content)
            
            # 3. Estrae parole chiave
            keywords = self.extract_keywords(content)
            
            # 4. Log dei risultati
            total_entities = sum(len(entity_list) for entity_list in entities.values())
            logger.info(f"Estratte {total_entities} entità e {len(keywords)} parole chiave")
            
            for entity_type, entity_list in entities.items():
                logger.info(f"  {entity_type}: {len(entity_list)} entità")
                for entity in entity_list[:3]:  # Mostra prime 3
                    logger.info(f"    - {entity['text']} (freq: {entity['frequency']})")
            
            # 5. Salva nel database
            success = self.save_entities(source_id, entities, keywords)
            
            return success
            
        except Exception as e:
            logger.error(f"Errore nel processamento della fonte {source_id}: {e}")
            return False

def main():
    """Funzione principale"""
    if len(sys.argv) != 2:
        print("Utilizzo: python improved_extract_entities.py <source_id>")
        sys.exit(1)
    
    try:
        source_id = int(sys.argv[1])
    except ValueError:
        logger.error("Source ID deve essere un numero intero")
        sys.exit(1)
    
    # Verifica connessione API
    if not api_client.check_health():
        logger.error("API non raggiungibile. Assicurati che il server sia in esecuzione.")
        sys.exit(1)
    
    # Crea l'estrattore e processa la fonte
    extractor = EntityExtractor()
    
    logger.info(f"=== Inizio estrazione entità per fonte ID: {source_id} ===")
    success = extractor.process_source(source_id)
    
    if success:
        logger.info(f"=== Estrazione entità completata per fonte {source_id} ===")
        sys.exit(0)
    else:
        logger.error(f"=== Errore nell'estrazione entità per fonte {source_id} ===")
        sys.exit(1)

if __name__ == "__main__":
    main()