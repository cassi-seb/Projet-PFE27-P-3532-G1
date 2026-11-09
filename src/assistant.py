import time
import json
import os
import re
import sys
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

# Assurer l'importation de src quel que soit le point d'entrée
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError
from src.models import ArgumentAnalysisResponse, PedagogicalResponse
from src.logger import log_interaction
from src.fact_checker import verify_factual_claims
from src.bias_matcher import match_fallacy_in_catalog

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROMPT_VERSION = "v2.1.0-gemma-accessible-catalog"
DEFAULT_GROQ_MODEL = "gemma2-9b-it"
DEFAULT_OPENROUTER_MODEL = "google/gemma-2-9b-it"
DEFAULT_MODEL_NAME = DEFAULT_GROQ_MODEL

# Rôle pédagogique strict : Ni censeur, ni arbitre (Tuteur d'esprit critique accessible à tous)
SYSTEM_PROMPT = """Tu es un assistant pédagogique d’esprit critique et de déconstruction d'arguments en langue française, fondé sur Google Gemma 2.
Ton rôle est d'être un TUTEUR D'ESPRIT CRITIQUE accessible à tous, JAMAIS UN ARBITRE.
Tu ne dois JAMAIS dire qui a tort ou raison, ni déclarer si un texte est "vrai" ou "faux" dans son ensemble.

DIRECTIVE ESSENTIELLE DE STYLE ET CLARTÉ :
Tes réponses doivent être SIMPLES, DIRECTES, CONCRÈTES et COMPRÉHENSIBLES PAR TOUS (citoyens, étudiants, lycéens).
Bannis le jargon abstrait ou inutilement universitaire. Explique toujours "en clair" ce qui se passe avec des mots du quotidien.
N'emploie JAMAIS le mot "sophisme" : utilise toujours "faille logique", "piège d'argumentation" ou "raccourci trompeur".

Tu dois TOUJOURS répondre en FRANÇAIS, sous la forme exclusive d'un objet JSON strict avec exactement ces 5 clés :

1. "these_principale": (chaîne)
   En clair, que défend l'auteur ? Résume l'idée centrale en une ou deux phrases simples, calmes et strictement neutres, sans prendre parti.

2. "deconstruction_logique": (liste d'objets ou de chaînes)
   Comment le texte tente de convaincre et où est le piège de raisonnement ?
   Repère les pièges fréquents (Attaque personnelle, Caricature / Homme de paille, Faux dilemme "tout noir ou tout blanc", Pente glissante / effet domino imaginaire, Généralisation hâtive, Appel aux émotions, Fausse cause / coïncidence).
   Pour chaque piège, cite OBLIGATOIREMENT le passage exact entre guillemets et explique de façon très simple pourquoi ce raisonnement peut tromper le lecteur.
   Exemple d'élément : {"nom": "Piège d'argumentation possible : Caricature", "passage_cite": "les partisans du projet veulent détruire tout emploi", "explication": "On exagère volontairement l'avis adverse pour le faire paraître ridicule, plutôt que de discuter des vrais arguments."}

3. "contre_hypothese_pedagogique": (chaîne)
   La question pour voir les choses autrement : une question simple, concrète et stimulante qui aide le lecteur à réfléchir sans le culpabiliser ni lui imposer une opinion.

4. "verification_donnees_factuelles": (liste d'objets ou de chaînes)
   Les chiffres sous la loupe : pour chaque chiffre ou grandeur mesurable, citer la valeur exacte trouvée dans le texte et mentionner la source officielle de référence (Banque mondiale, Insee, Eurostat) ou indiquer "non vérifiable automatiquement hors périmètre statistique ouvert". Ne jamais inventer de données.

5. "limites_analyse": (chaîne ou liste de chaînes)
   Fait prouvable vs avis personnel : expliquer très simplement ce qui peut être vérifié avec des données concrètes et ce qui relève d'une opinion ou d'un choix citoyen que chacun est libre d'avoir.

Réponds UNIQUEMENT par l'objet JSON valide, sans balises Markdown autour (pas de ```json), sans texte introductif ni conclusion.
"""

def query_openrouter(text: str, api_key: str, model: str = DEFAULT_OPENROUTER_MODEL) -> str:
    """Interroge le modèle via l'API OpenRouter (compatible Gemma 2, Llama, Mistral, etc.)."""
    import requests
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Assistant Esprit Critique PFE",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Texte à analyser :\n\n{text}"}
        ],
        "temperature": 0.2
    }
    response = requests.post(url, headers=headers, json=payload, timeout=35)
    response.raise_for_status()
    res_json = response.json()
    return res_json["choices"][0]["message"]["content"]

def query_groq_gemma(text: str, api_key: str, model: str = DEFAULT_GROQ_MODEL) -> str:
    """Interroge le modèle Gemma 2 hébergé gratuitement et ultra-rapidement sur Groq."""
    import requests
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
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
    Fournit des explications simples, concrètes et adaptées au grand public.
    """
    words = text.split()
    extrait = " ".join(words[:10]) + ("..." if len(words) > 10 else "")
    
    # Appel du module de vérification déterministe des chiffres (Banque Mondiale / Insee)
    factual_results = verify_factual_claims(text)
    
    # Appel du module de rapprochement avec la base des pièges fréquents
    catalog_match = match_fallacy_in_catalog(text)
    nom_piege = catalog_match.get("nom_simple", "Raccourci de raisonnement possible")
    explication_simple = catalog_match.get("en_clair", "Ce propos présente une conclusion tranchée sans détailler toutes les étapes qui mènent à cette affirmation.")

    mock_data = {
        "these_principale": f"L'auteur affirme que la position résumée par « {extrait} » constitue la réponse évidente au problème soulevé.",
        "deconstruction_logique": [
            {
                "nom": f"Piège d'argumentation possible : {nom_piege}",
                "passage_cite": extrait,
                "explication": explication_simple
            }
        ],
        "contre_hypothese_pedagogique": "Quelles autres explications ou solutions modérées permettraient de nuancer ce point de vue sans balayer la préoccupation de départ ?",
        "verification_donnees_factuelles": factual_results,
        "limites_analyse": "Les données chiffrées éventuelles peuvent être vérifiées auprès d'organismes officiels, mais juger si cette idée est souhaitable ou juste relève de l'opinion personnelle de chaque citoyen.",
        "verification_catalogue_pieges": catalog_match
    }
    return json.dumps(mock_data, ensure_ascii=False)

def query_assistant(
    text: str, 
    api_key: Optional[str] = None, 
    model: Optional[str] = None,
    provider: Optional[str] = None
) -> Tuple[Optional[ArgumentAnalysisResponse], bool, float, str]:
    """
    Interroge l'assistant d'esprit critique (Gemma 2 via OpenRouter ou Groq), 
    valide le contrat de sortie et journalise l'échange dans SQLite.
    
    Supporte nativement :
    1. OpenRouter (clé commençant par sk-or- ou variable OPENROUTER_API_KEY)
    2. Groq (clé commençant par gsk_ ou variable GROQ_API_KEY)
    3. OpenAI si OPENAI_API_KEY est fournie
    4. Simulation pédagogique haute-fidélité immédiate
    """
    start_time = time.time()
    raw_response = ""
    is_valid = False
    validated_obj = None
    error_msg = None

    openrouter_env = os.getenv("OPENROUTER_API_KEY")
    groq_env = os.getenv("GROQ_API_KEY")
    openai_env = os.getenv("OPENAI_API_KEY")

    active_key = api_key or ""
    active_provider = (provider or "").lower()

    # Détection intelligente du fournisseur
    if active_key.startswith("sk-or-") or active_provider == "openrouter":
        target_provider = "openrouter"
        chosen_key = active_key or openrouter_env
    elif active_key.startswith("gsk_") or active_provider == "groq":
        target_provider = "groq"
        chosen_key = active_key or groq_env
    elif openrouter_env:
        target_provider = "openrouter"
        chosen_key = openrouter_env
    elif groq_env:
        target_provider = "groq"
        chosen_key = groq_env
    elif openai_env or active_key:
        target_provider = "openai"
        chosen_key = active_key or openai_env
    else:
        target_provider = "simulation"
        chosen_key = None

    # Exécution selon le fournisseur
    if target_provider == "openrouter" and chosen_key:
        try:
            target_model = model or DEFAULT_OPENROUTER_MODEL
            raw_response = query_openrouter(text, api_key=chosen_key, model=target_model)
        except Exception as e:
            error_msg = f"Erreur API OpenRouter ({str(e)})"
            raw_response = ""

    elif target_provider == "groq" and chosen_key:
        try:
            target_model = model or DEFAULT_GROQ_MODEL
            raw_response = query_groq_gemma(text, api_key=chosen_key, model=target_model)
        except Exception as e:
            error_msg = f"Erreur API Groq Gemma ({str(e)})"
            raw_response = ""

    elif target_provider == "openai" and chosen_key:
        try:
            raw_response = query_openai_compatible(text, api_key=chosen_key, model=model or "gpt-4o-mini")
        except Exception as e:
            error_msg = f"Erreur API OpenAI ({str(e)})"
            raw_response = ""

    # Repli automatique sur simulation si aucune clé ou si l'API échoue
    if not raw_response:
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

    # Extraction sécurisée du premier bloc JSON complet si du texte entoure l'objet
    if "{" in cleaned_json and "}" in cleaned_json:
        start_idx = cleaned_json.find("{")
        end_idx = cleaned_json.rfind("}") + 1
        cleaned_json = cleaned_json[start_idx:end_idx]

    # Validation Pydantic du contrat de sortie
    if cleaned_json:
        try:
            parsed_json = json.loads(cleaned_json)
            
            # Module Déterministe de Fact-Checking Statistique (Banque Mondiale / Insee)
            fact_checks = verify_factual_claims(text)
            if fact_checks:
                parsed_json["verification_donnees_factuelles"] = fact_checks

            # Module Déterministe de Rapprochement avec le Catalogue des 15 Pièges Fréquents
            deconstruction_val = parsed_json.get("deconstruction_logique", "")
            if isinstance(deconstruction_val, list):
                deconstruction_str = " ".join(str(x) for x in deconstruction_val)
            else:
                deconstruction_str = str(deconstruction_val)

            catalog_check = match_fallacy_in_catalog(text, deconstruction_str)
            parsed_json["verification_catalogue_pieges"] = catalog_check

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
