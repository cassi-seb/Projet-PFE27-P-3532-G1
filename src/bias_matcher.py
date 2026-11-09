"""
Module de détection et de rapprochement avec le catalogue de référence des pièges d'argumentation fréquents.
Conforme au fichier `data/fallacy_catalog.jsonl` (15 pièges fréquents).
Fournit des explications simples, concrètes et accessibles au grand public (sans jargon abstrait).
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "fallacy_catalog.jsonl"

# Fiches pédagogiques simplifiées pour le grand public (accessibles à tous)
PEDAGOGICAL_PROFILES = {
    "Ad hominem": {
        "nom_simple": "Attaque personnelle (au lieu de critiquer l'idée)",
        "en_clair": "On s'en prend directement à la personne (son passé, son physique, sa vie privée) pour discréditer son avis, plutôt que d'examiner si ce qu'elle dit est vrai ou faux.",
        "pourquoi_trompeur": "Cela détourne l'attention : même si une personne a des défauts, ce qu'elle dit peut tout de même être pertinent ou vérifié.",
        "astuce_reconnaitre": "Repérez si la critique vise l'auteur (« il est incompétent », « regardez qui parle ») plutôt que le fond du dossier."
    },
    "Appel à l'autorité": {
        "nom_simple": "Fausse autorité (ou expert hors de son domaine)",
        "en_clair": "On affirme qu'une idée est forcément vraie parce qu'une personne célèbre, un grand scientifique ou une figure connue l'a dit, même si ce n'est pas du tout sa spécialité.",
        "pourquoi_trompeur": "La notoriété ou les diplômes dans un domaine (ex. physique) ne garantissent pas qu'on ait raison dans un autre (ex. médecine ou économie).",
        "astuce_reconnaitre": "Demandez-vous : « Cette personne est-elle vraiment experte qualifiée sur ce sujet précis et ses affirmations reposent-elles sur des preuves ? »"
    },
    "Appel à l'émotion": {
        "nom_simple": "Coup de massue émotionnel (culpabilité, pitié)",
        "en_clair": "On fait vibrer la corde sensible (images touchantes, pitié, colère, culpabilité) pour forcer l'adhésion sans donner de preuves logiques.",
        "pourquoi_trompeur": "L'émotion submerge la réflexion rationnelle et pousse à réagir impulsivement sans peser le pour et le contre.",
        "astuce_reconnaitre": "Séparez ce que vous ressentez (tristesse, indignation) des faits réels présentés pour juger de la mesure proposée."
    },
    "Appel à la nature": {
        "nom_simple": "« C'est naturel donc c'est bon »",
        "en_clair": "On décrète qu'une chose est forcément saine et inoffensive parce qu'elle vient de la nature, et que tout ce qui est fabriqué par l'homme est dangereux.",
        "pourquoi_trompeur": "Beaucoup de poisons mortels (champignons vénéneux, venins) sont 100% naturels, tandis que des produits créés en laboratoire (vaccins, antibiotiques) sauvent des vies.",
        "astuce_reconnaitre": "Rappelez-vous : « naturel » n'est pas synonyme d'« inoffensif » ni de « bénéfique »."
    },
    "Appel à la tradition": {
        "nom_simple": "« On a toujours fait comme ça »",
        "en_clair": "On soutient qu'une pratique ou une idée est bonne simplement parce qu'elle existe depuis longtemps et que les anciens faisaient ainsi.",
        "pourquoi_trompeur": "L'ancienneté d'une habitude ne prouve en rien son efficacité ou sa justice : de nombreuses erreurs ont duré des siècles avant d'être corrigées.",
        "astuce_reconnaitre": "Posez la question : « Quels sont les bénéfices concrets réels aujourd'hui, au-delà de l'habitude ? »"
    },
    "Raisonnement circulaire": {
        "nom_simple": "Tourner en rond (la conclusion est dans la preuve)",
        "en_clair": "On tente de prouver une affirmation en répétant simplement la même idée sous une autre forme, sans apporter aucun fait nouveau.",
        "pourquoi_trompeur": "La phrase donne l'illusion d'une explication solide alors qu'elle ne fait que répéter son point de départ en boucle.",
        "astuce_reconnaitre": "Cherchez la preuve extérieure : si la phrase revient au point de départ (« c'est bien parce que c'est super »), rien n'a été prouvé."
    },
    "Faux dilemme": {
        "nom_simple": "Piège du « Tout noir ou tout blanc »",
        "en_clair": "On enferme le choix entre deux seules options extrêmes (souvent l'option voulue contre une catastrophe), en cachant toutes les autres solutions possibles au milieu.",
        "pourquoi_trompeur": "Le cerveau préfère les choix simples, mais le monde réel offre presque toujours des compromis ou des troisièmes voies.",
        "astuce_reconnaitre": "Guettez les expressions « Soit... soit », « Il n'y a que deux choix » : demandez-vous s'il n'existe pas une option intermédiaire."
    },
    "Généralisation hâtive": {
        "nom_simple": "Tirer une règle générale d'un seul cas",
        "en_clair": "On prend une mauvaise expérience vécue ou un seul exemple marquant pour en faire une vérité absolue sur tout un groupe ou tout un métier.",
        "pourquoi_trompeur": "Un exemple isolé ne représente jamais une tendance générale statistique.",
        "astuce_reconnaitre": "Méfiez-vous des mots comme « tous », « jamais », « chaque fois » dès qu'ils s'appuient sur une simple anecdote."
    },
    "Pente glissante": {
        "nom_simple": "Effet boule de neige imaginaire",
        "en_clair": "On affirme qu'une petite décision anodine mènera inévitablement et par réaction en chaîne à un désastre total, sans prouver les étapes.",
        "pourquoi_trompeur": "Cela fait peur en reliant artificiellement une action modérée à un scénario apocalyptique.",
        "astuce_reconnaitre": "Vérifiez chaque maillon de la chaîne : est-ce vraiment certain que l'étape 1 entraîne automatiquement l'étape 5 ?"
    },
    "Homme de paille": {
        "nom_simple": "Caricature (déformer les propos de l'autre)",
        "en_clair": "On déforme, simplifie ou exagère la position de l'adversaire pour créer une version ridicule facile à détruire, qu'il n'a pourtant jamais soutenue.",
        "pourquoi_trompeur": "Le public croit que l'argument a été battu, alors que seule une version inventée a été réfutée.",
        "astuce_reconnaitre": "Vérifiez toujours ce que la personne opposée a réellement dit dans son texte d'origine."
    },
    "Whataboutisme": {
        "nom_simple": "« Et vous alors ? » (Faire diversion)",
        "en_clair": "Au lieu de répondre à une critique ou un reproche, on attaque immédiatement l'autre sur un autre dossier pour éviter le problème.",
        "pourquoi_trompeur": "Les deux erreurs ne s'annulent pas : détourner la conversation empêche de régler le problème soulevé au départ.",
        "astuce_reconnaitre": "Repérez si la réponse commence par « Et vous alors ? », « Qu'avez-vous fait en l'an X ? » sans répondre à la question posée."
    },
    "Appel à la popularité": {
        "nom_simple": "L'effet de foule (« Tout le monde le dit »)",
        "en_clair": "On affirme qu'une idée est vraie ou qu'une décision est bonne simplement parce qu'un grand nombre de personnes ou des millions d'utilisateurs la partagent.",
        "pourquoi_trompeur": "Une idée fausse reste fausse, même si des millions de gens y croient (la Terre n'était pas plate quand la majorité le pensait).",
        "astuce_reconnaitre": "Posez la question : « Quels sont les arguments scientifiques et les faits objectifs, indépendamment du nombre de likes ou de partisans ? »"
    },
    "Appel à la peur": {
        "nom_simple": "Faire paniquer pour forcer l'accord",
        "en_clair": "On agite une menace imminente et terrifiante pour inciter les gens à accepter une mesure radicale sous l'effet de l'urgence et de la peur.",
        "pourquoi_trompeur": "La panique court-circuite la réflexion critique et empêche d'examiner si la mesure proposée est proportionnée et efficace.",
        "astuce_reconnaitre": "Distinguez un danger réel documenté d'une dramatisation anxiogène destinée à bloquer la discussion."
    },
    "Post hoc": {
        "nom_simple": "Confusion entre suite chronologique et cause réelle",
        "en_clair": "On s'imagine que parce qu'un événement B arrive juste après un événement A, c'est forcément A qui a provoqué B.",
        "pourquoi_trompeur": "Deux événements peuvent se suivre par pure coïncidence ou être causés tous deux par un troisième facteur invisible.",
        "astuce_reconnaitre": "Ne confondez pas « après cela » et « à cause de cela » : cherchez le mécanisme de cause à effet vérifié."
    },
    "Hareng rouge": {
        "nom_simple": "Diversion hors-sujet",
        "en_clair": "On lance brusquement un sujet annexe captivant ou polémique pour noyer le poisson et faire oublier la question principale embarrassante.",
        "pourquoi_trompeur": "L'attention se déplace sur une autre dispute et la question de fond initiale reste sans réponse.",
        "astuce_reconnaitre": "Rappelez-vous le sujet de départ et demandez : « Est-ce que ce nouvel élément répond vraiment au problème posé ? »"
    }
}

def load_raw_catalog() -> List[Dict[str, Any]]:
    """Charge les 15 entrées brutes du catalogue JSONL."""
    entries = []
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
    return entries

def match_fallacy_in_catalog(
    text: str, 
    deconstruction_text: str = ""
) -> Dict[str, Any]:
    """
    Rapproche le texte et la déconstruction logique avec la base de référence des 15 pièges fréquents.
    Retourne une analyse claire, simple et pédagogique, accessible à tous.
    """
    catalog = load_raw_catalog()
    combined_content = f"{text} {deconstruction_text}".lower()

    # Mappage des correspondances de détection
    fallacy_keywords = {
        "Ad hominem": ["ad hominem", "attaque personnelle", "incompétence", "candidat", "ivresse", "condamné", "crédit", "personne", "casier"],
        "Appel à l'autorité": ["autorité", "professeur", "expert", "spécialiste", "nobel", "forcément raison", "éminent"],
        "Appel à l'émotion": ["émotion", "enfants", "petits enfants", "larmes", "pitié", "chèque", "hésiter une seule seconde", "affamés"],
        "Appel à la nature": ["nature", "naturel", "naturelle", "plantes", "100%", "sauvages", "artificiel", "chimique"],
        "Appel à la tradition": ["tradition", "toujours", "ancêtres", "siècles", "foyer", "coutume", "nos aïeux"],
        "Raisonnement circulaire": ["circulaire", "chef-d'œuvre", "extraordinaire", "en rond", "parce que c'est", "prouve que"],
        "Faux dilemme": ["soit", "ou bien", "deux seules", "faillite", "coupons", "alternative", "intermédiaire", "avec nous ou contre"],
        "Généralisation hâtive": ["tous les", "généralisation", "tous des", "arnaqué", "plombier", "premier", "chaque fois"],
        "Pente glissante": ["pente glissante", "domino", "dictature", "engrenage", "cannabis", "héroïne", "addiction généralisée", "c'est le début"],
        "Homme de paille": ["homme de paille", "caricature", "veulent détruire", "déformer", "ruiner tous", "loyers", "partisans"],
        "Whataboutisme": ["whataboutisme", "et vous", "et vous alors", "scandale", "renvoyer", "accusez", "regardez-vous"],
        "Appel à la popularité": ["popularité", "millions", "tout le monde", "régime miracle", "tant de gens", "foule", "majorité"],
        "Appel à la peur": ["peur", "terroristes", "sécurité", "menace", "panique", "danger immédiat", "aucun d'entre vous"],
        "Post hoc": ["post hoc", "bracelet", "depuis lors", "mal de dos", "coïncidence", "après que", "m'a guéri", "cause"],
        "Hareng rouge": ["hareng rouge", "diversion", "licencié", "innovation durable", "détourner", "autre sujet", "plutôt parler"]
    }

    best_match_key = None
    best_score = 0
    detected_words = []

    for f_type, kws in fallacy_keywords.items():
        score = 0
        matched_for_this = []
        for kw in kws:
            if kw in combined_content:
                score += 1
                matched_for_this.append(kw)
        if score > best_score:
            best_score = score
            best_match_key = f_type
            detected_words = matched_for_this

    if best_match_key and best_score >= 1:
        entry = next((e for e in catalog if e.get("fallacy_type") == best_match_key), None)
        profile = PEDAGOGICAL_PROFILES.get(best_match_key, {})

        return {
            "est_dans_catalogue": True,
            "id_reference": entry.get("id", "F-REF") if entry else "F-REF",
            "type_technique": best_match_key,
            "nom_simple": profile.get("nom_simple", best_match_key),
            "en_clair": profile.get("en_clair", "Ce piège simplifie le problème pour imposer une conclusion sans donner de preuve solide."),
            "pourquoi_trompeur": profile.get("pourquoi_trompeur", "Il pousse à réagir par automatisme mental plutôt qu'avec discernement."),
            "astuce_reconnaitre": profile.get("astuce_reconnaitre", "Prenez du recul et isolez la preuve concrète."),
            "exemple_reference": entry.get("text", "") if entry else "",
            "mots_declencheurs": detected_words[:4]
        }

    # Cas où aucun des 15 pièges classiques n'est clairement détecté
    return {
        "est_dans_catalogue": False,
        "id_reference": None,
        "type_technique": "Hors des 15 pièges fréquents",
        "nom_simple": "Aucun piège fréquent classique identifié",
        "en_clair": "Le texte ne reproduit pas l'un des 15 pièges d'argumentation les plus fréquents de notre base de référence.",
        "pourquoi_trompeur": "L'argumentation repose soit sur des faits vérifiables, soit sur un point de vue plus nuancé qui ne tombe pas dans un piège classique.",
        "astuce_reconnaitre": "Restez attentif aux chiffres cités et vérifiez s'ils s'appuient sur des sources indépendantes vérifiées.",
        "exemple_reference": None,
        "mots_declencheurs": []
    }

if __name__ == "__main__":
    test1 = "Soit nous coupons les aides, soit notre pays fera faillite d'ici six mois !"
    print("Test 1 (Faux dilemme) :", json.dumps(match_fallacy_in_catalog(test1), ensure_ascii=False, indent=2))
    test2 = "Regardez ces images de petits enfants affamés, signez ce chèque !"
    print("Test 2 (Appel émotion) :", json.dumps(match_fallacy_in_catalog(test2), ensure_ascii=False, indent=2))
