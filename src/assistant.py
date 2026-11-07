import time
import json
import os
import re
import sys
from pathlib import Path
from typing import Tuple, Optional

# Assurer l'importation de src quel que soit le point d'entrée
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError
from src.models import ArgumentAnalysisResponse, PedagogicalResponse
from src.logger import log_interaction
from src.fact_checker import verify_factual_claims

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROMPT_VERSION = "v2.0.0-gemma-argument-analysis"
DEFAULT_MODEL_NAME = "gemma2-9b-it"

# Rôle pédagogique strict : Ni censeur, ni arbitre (Tuteur d'esprit critique)
SYSTEM_PROMPT = """Tu es un assistant pédagogique d’esprit critique et de déconstruction d’arguments en langue française, fondé sur le modèle Google Gemma 2.
Ton rôle est d'être un TUTEUR D'ESPRIT CRITIQUE, JAMAIS UN ARBITRE.
Tu ne dois JAMAIS dire qui a tort ou raison, ni déclarer si un texte est "vrai" ou "faux" dans son ensemble.

Tu dois TOUJOURS répondre en FRANÇAIS, sous la forme exclusive d'un objet JSON strict avec exactement ces 5 clés :

1. "these_principale": (chaîne)
   Reformulation synthétique, claire et strictement neutre de la thèse centrale défendue dans le texte, sans adjectif polarisant ni parti pris.

2. "deconstruction_logique": (liste d'objets ou de chaînes)
   Analyse de la mécanique argumentative. Si une faille logique, un piège d'argumentation ou un raccourci trompeur est soupçonné (parmi : Attaque personnelle / Ad hominem, Caricature de la position adverse, Faux dilemme / deux seules options présentées, Effet domino / Pente glissante, Généralisation hâtive, Appel aux émotions, Fausse cause / coïncidence confondue avec cause), tu dois TOUJOURS citer le passage textuel exact entre guillemets et utiliser la formule de prudence "Faille logique possible" ou "Piège d'argumentation possible" :
   Exemple d'élément : {"nom": "Piège d'argumentation possible : Caricature", "passage_cite": "les partisans du projet veulent détruire tout emploi", "explication": "Déformation excessive de la position opposée pour la rejeter plus facilement."}

3. "contre_hypothese_pedagogique": (chaîne)
   Une question contradictoire stimulante et bienveillante ou une perspective alternative qui incite le lecteur à approfondir sa réflexion par lui-même, sans jamais le braquer ni imposer une opinion.

4. "verification_donnees_factuelles": (liste d'objets ou de chaînes)
   Repérage des données chiffrées, dates ou grandeurs mesurables. Pour chaque chiffre :
   - Citer la valeur trouvée dans le texte.
   - Mentionner la source de référence ouverte appropriée (Insee, Banque mondiale, Eurostat) ou indiquer explicitement "non vérifiable automatiquement hors périmètre statistique ouvert".
   - Ne JAMAIS inventer de données non présentes.

5. "limites_analyse": (chaîne ou liste de chaînes)
   Distinction méthodique entre ce qui relève du fait matériel vérifiable et ce qui relève du jugement de valeur, de la préférence politique ou morale, en rappelant que le jugement de valeur appartient au lecteur citoyen.

Réponds UNIQUEMENT par l'objet JSON valide, sans balises Markdown autour (pas de ```json), sans texte introductif ni conclusion.
"""

def query_groq_gemma(text: str, api_key: str, model: str = DEFAULT_MODEL_NAME) -> str:
    """Interroge le modèle Gemma 2 hébergé gratuitement et ultra-rapidement sur Groq."""
    import requests
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Texte à analyser :\n\n{text}"}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def query_openai_compatible(text: str, api_key: str, model: str = "gpt-4o-mini", base_url: Optional[str] = None) -> str:
    """Interroge un endpoint compatible OpenAI / OpenRouter."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Texte à analyser :\n\n{text}"}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    return completion.choices[0].message.content or ""

def generate_pedagogical_simulation(text: str) -> str:
    """
    Simulation pédagogique d'esprit critique haute-fidélité (0 latence, 0 dépendance externe).
    Intègre le module déterministe de fact-checking ouvert (Banque Mondiale / Insee).
    """
    words = text.split()
    extrait = " ".join(words[:10]) + ("..." if len(words) > 10 else "")
    
    # Appel du module de vérification déterministe des chiffres (O5)
    factual_results = verify_factual_claims(text)

    mock_data = {
        "these_principale": f"L'argumentation présentée affirme que la position défendue (« {extrait} ») constitue la seule voie cohérente face aux enjeux décrits.",
        "deconstruction_logique": [
            {
                "nom": "Prémisse initiale identifiée",
                "passage_cite": extrait,
                "explication": "Le propos pose comme point de départ une relation de cause à effet directe sans exposer les variables intermédiaires."
            },
            {
                "nom": "Faille logique possible : Raccourci ou Faux dilemme",
                "passage_cite": extrait,
                "explication": "Tendance à restreindre le débat à deux options opposées ou à généraliser à partir d'un constat particulier."
            }
        ],
        "contre_hypothese_pedagogique": "Quelles données ou perspectives alternatives permettraient de nuancer ce point de vue sans balayer la préoccupation initiale de l'auteur ?",
        "verification_donnees_factuelles": factual_results,
        "limites_analyse": "L'analyse isole les affirmations mesurables mais rappelle que le jugement d'opportunité, d'éthique ou de justice relève de l'appréciation propre du citoyen."
    }
    return json.dumps(mock_data, ensure_ascii=False)

def query_assistant(
    text: str, 
    api_key: Optional[str] = None, 
    model: Optional[str] = None
) -> Tuple[Optional[ArgumentAnalysisResponse], bool, float, str]:
    """
    Interroge l'assistant d'esprit critique (Gemma 2), valide le contrat de sortie
    et journalise l'échange dans SQLite.
    
    Ordre de priorité (100% SANS Ollama) :
    1. API Groq gratuite pour Gemma 2 (gemma2-9b-it) si GROQ_API_KEY est définie
    2. API OpenAI / OpenRouter si OPENAI_API_KEY est fournie
    3. Simulation pédagogique haute-fidélité immédiate (aucun coût, aucune dépendance)
    
    Retourne : (reponse_validee, est_json_valide, latence_ms, contenu_brut)
    """
    start_time = time.time()
    raw_response = ""
    is_valid = False
    validated_obj = None
    error_msg = None

    # Détection de la clé Groq (soit variable GROQ_API_KEY, soit api_key passée commençant par gsk_)
    groq_key = os.getenv("GROQ_API_KEY")
    if api_key:
        if api_key.startswith("gsk_") or not groq_key:
            groq_key = api_key

    openai_key = api_key or os.getenv("OPENAI_API_KEY")

    # 1. Utilisation de Gemma 2 via Groq API (gratuit, ultra-rapide)
    if groq_key:
        try:
            target_model = model or DEFAULT_MODEL_NAME
            raw_response = query_groq_gemma(text, api_key=groq_key, model=target_model)
        except Exception as e:
            error_msg = f"Erreur API Groq Gemma : {str(e)}"
            raw_response = ""

    # 2. Repli sur OpenAI / OpenRouter si disponible
    elif openai_key:
        try:
            raw_response = query_openai_compatible(text, api_key=openai_key, model=model or "gpt-4o-mini")
        except Exception as e:
            error_msg = f"Erreur API Cloud : {str(e)}"
            raw_response = ""

    # 3. Repli automatique et immédiat sur la simulation haute-fidélité
    if not raw_response and not error_msg:
        raw_response = generate_pedagogical_simulation(text)

    latency_ms = (time.time() - start_time) * 1000.0

    # Nettoyage Markdown éventuel
    cleaned_json = raw_response.strip()
    if cleaned_json.startswith("```json"):
        cleaned_json = cleaned_json[7:]
    elif cleaned_json.startswith("```"):
        cleaned_json = cleaned_json[3:]
    if cleaned_json.endswith("```"):
        cleaned_json = cleaned_json[:-3]
    cleaned_json = cleaned_json.strip()

    # Validation Pydantic du contrat à 5 champs
    if cleaned_json:
        try:
            parsed_json = json.loads(cleaned_json)
            
            # Module Déterministe de Fact-Checking Statistique (Objectif O5) :
            # Les données officielles proviennent TOUJOURS de l'API Banque Mondiale / Insee, JAMAIS du LLM
            fact_checks = verify_factual_claims(text)
            if fact_checks:
                parsed_json["verification_donnees_factuelles"] = fact_checks

            validated_obj = ArgumentAnalysisResponse(**parsed_json)
            is_valid = True
        except (json.JSONDecodeError, ValidationError) as e:
            is_valid = False
            error_msg = f"Erreur validation contrat JSON : {str(e)}"

    # Journalisation SQLite intégrale (100% de traçabilité)
    log_interaction(
        prompt_version=PROMPT_VERSION,
        user_question=text,
        raw_response=raw_response,
        is_valid_json=is_valid,
        latency_ms=latency_ms,
        error_message=error_msg
    )

    return validated_obj, is_valid, latency_ms, raw_response
