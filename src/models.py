from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, field_validator

class FailleLogiqueItem(BaseModel):
    nom: str = Field(..., description="Nom de la faille logique ou du piège d'argumentation (ex: Caricature, Faux dilemme, Attaque personnelle).")
    passage_cite: str = Field(..., description="Extrait textuel précis illustrant ce raccourci.")
    explication: str = Field(..., description="Explication neutre du problème de raisonnement.")

# Alias pour compatibilité
SophismeItem = FailleLogiqueItem

class ArgumentAnalysisResponse(BaseModel):
    """
    Contrat de sortie strict imposé à l'assistant d'esprit critique (Modèle Gemma).
    Chaque analyse d'argument doit respecter cette structure en 5 blocs standardisés.
    """
    these_principale: str = Field(
        ..., 
        description="Reformulation neutre et synthétique de la thèse défendue par l'auteur."
    )
    deconstruction_logique: Union[str, List[Union[str, Dict[str, Any]]]] = Field(
        ..., 
        description="Décomposition méthodique du raisonnement (prémisses, enchaînements et failles logiques avec citation exacte)."
    )
    contre_hypothese_pedagogique: str = Field(
        ..., 
        description="Question ou perspective contradictoire amenant le lecteur à réfléchir sans prise de position partisane."
    )
    verification_donnees_factuelles: Union[str, List[Union[str, Dict[str, Any]]]] = Field(
        ..., 
        description="Chiffres et données quantitatives cités, avec mention de la source officielle (Insee, Eurostat, Banque mondiale) ou 'non vérifiable automatiquement'."
    )
    limites_analyse: Union[str, List[str]] = Field(
        ..., 
        description="Distinction explicite entre ce qui relève du fait vérifiable et ce qui relève du jugement de valeur / opinion."
    )
    verification_catalogue_pieges: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Vérification et rapprochement avec la base des 15 pièges d'argumentation les plus fréquents (fallacy_catalog)."
    )

    @field_validator("these_principale", mode="before")
    def sanitize_these(cls, v):
        if isinstance(v, dict):
            return v.get("these") or v.get("resume") or str(v)
        return str(v).strip()

    @field_validator("contre_hypothese_pedagogique", mode="before")
    def sanitize_contre_hypothese(cls, v):
        if isinstance(v, dict):
            return v.get("question") or v.get("hypothese") or str(v)
        return str(v).strip()

    @field_validator("limites_analyse", mode="before")
    def format_limites(cls, v):
        if isinstance(v, list):
            return "\n".join(f"- {item}" for item in v)
        if isinstance(v, dict):
            return "\n".join(f"- {k}: {val}" for k, val in v.items())
        return str(v).strip()

    @field_validator("deconstruction_logique", mode="before")
    def sanitize_deconstruction(cls, v):
        if isinstance(v, list):
            formatted = []
            for item in v:
                if isinstance(item, dict):
                    nom = item.get("nom") or item.get("faille") or item.get("piege") or "Faille logique possible"
                    citation = item.get("citation") or item.get("passage_cite") or ""
                    explication = item.get("explication") or item.get("description") or ""
                    if citation:
                        formatted.append(f"**{nom}** : « *{citation}* » — {explication}")
                    else:
                        formatted.append(f"**{nom}** : {explication}")
                else:
                    formatted.append(str(item))
            return "\n".join(f"- {line}" for line in formatted)
        return str(v).strip()

    @field_validator("verification_donnees_factuelles", mode="before")
    def sanitize_donnees(cls, v):
        if isinstance(v, list):
            formatted = []
            for item in v:
                if isinstance(item, dict):
                    chiffre_texte = item.get("chiffre_texte") or item.get("chiffre") or ""
                    chiffre_officiel = item.get("chiffre_officiel")
                    verdict_clair = item.get("verdict_clair")
                    source = item.get("source") or "Banque Mondiale & Insee"
                    
                    if item.get("type_verification") == "comparaison_disponible" and chiffre_officiel and chiffre_officiel != "N/A":
                        formatted.append(
                            f"📊 Chiffre avancé dans le texte : {chiffre_texte}\n"
                            f"🏛️ Réalité officielle mesurée : {chiffre_officiel}\n"
                            f"⚖️ Constat : {verdict_clair}\n"
                            f"📚 Source : {source}"
                        )
                    elif verdict_clair:
                        formatted.append(f"ℹ️ {verdict_clair}")
                    elif item.get("analyse"):
                        formatted.append(f"• {item.get('analyse')}")
                    else:
                        formatted.append(f"• Chiffre : {chiffre_texte} ({source})")
                else:
                    formatted.append(str(item))
            return "\n\n".join(formatted)
        return str(v).strip()
        return str(v).strip()

# Alias pour rétro-compatibilité
PedagogicalResponse = ArgumentAnalysisResponse
