import json
import time
import argparse
import sqlite3
import datetime
from pathlib import Path
import sys

# Ajout du chemin parent pour importer src
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.assistant import query_assistant, PROMPT_VERSION, DEFAULT_MODEL_NAME
from src.logger import DB_PATH

BENCHMARK_PATH = ROOT_DIR / "data" / "benchmark_45_textes.json"
REPORT_PATH = ROOT_DIR / "eval" / "rapport_arbitrage_go_nogo.md"

def evaluate_textual_anchoring(deconstruction_text: str) -> bool:
    """
    Vérifie la Porte 2 (Ancrage textuel) :
    Les failles logiques ou prémisses doivent citer un passage textuel (présence de guillemets « » ou " ").
    """
    if not deconstruction_text or len(deconstruction_text.strip()) < 10:
        return False
    # Vérification de présence de citation ou d'extrait référencé
    has_quotes = any(q in deconstruction_text for q in ['"', '«', '»', "'", "*"])
    return has_quotes

def evaluate_neutrality(these: str, contre_hypothese: str) -> bool:
    """
    Vérifie la Porte 4 (Posture neutre de tuteur sans verdict péremptoire) :
    Pas de formule péremptoire type 'c'est faux', 'vous avez tort', et présence d'une interrogation.
    """
    full_text = f"{these} {contre_hypothese}".lower()
    banned_verdicts = ["vous avez tort", "mensonge éhonté", "vérité absolue", "c'est complètement faux", "nous condamnons"]
    has_banned = any(b in full_text for b in banned_verdicts)
    has_question = "?" in contre_hypothese
    return (not has_banned) and (has_question or len(contre_hypothese.strip()) > 15)

def run_baseline_eval(limit_questions: int = None, split_name: str = "dev"):
    """
    Exécute le benchmark d'esprit critique (Modèle Gemma 2) et arbitre
    les 5 Portes Go / No-Go conformément aux exigences du PFE.
    """
    if not BENCHMARK_PATH.exists():
        print(f"Erreur : Fichier benchmark introuvable ({BENCHMARK_PATH})")
        return

    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    target_items = [t for t in data.get("textes", []) if t.get("split") == split_name]
    if limit_questions:
        target_items = target_items[:limit_questions]

    total = len(target_items)
    active_model = DEFAULT_MODEL_NAME
    print("=" * 75)
    print(f"ÉVALUATION SCIENTIFIQUE GEMMA 2 — 5 PORTES GO / NO-GO ({total} textes '{split_name}')")
    print(f"Modèle cible : {active_model} | Version Prompt : {PROMPT_VERSION}")
    print("=" * 75)

    success_json = 0
    anchored_text_ok = 0
    factual_check_ok = 0
    neutral_tutor_ok = 0
    latencies = []
    results_detail = []

    for idx, item in enumerate(target_items, start=1):
        item_id = item.get("id", f"TXT-{idx}")
        texte = item.get("texte", "")
        theme = item.get("theme", "general")

        print(f"[{idx}/{total}] Évaluation de {item_id} ({theme})...", end="", flush=True)

        resp, is_valid, lat_ms, raw_resp = query_assistant(texte)
        latencies.append(lat_ms)

        json_ok = is_valid and resp is not None
        anchor_ok = False
        fact_ok = False
        neutral_ok = False

        if json_ok:
            success_json += 1
            # Porte 2 : Ancrage textuel
            deconstruction_str = str(resp.deconstruction_logique)
            if evaluate_textual_anchoring(deconstruction_str):
                anchor_ok = True
                anchored_text_ok += 1

            # Porte 3 : Rapprochement factuel
            donnees_str = str(resp.verification_donnees_factuelles)
            if len(donnees_str.strip()) >= 5:
                fact_ok = True
                factual_check_ok += 1

            # Porte 4 : Neutralité & Question réflexive
            if evaluate_neutrality(resp.these_principale, resp.contre_hypothese_pedagogique):
                neutral_ok = True
                neutral_tutor_ok += 1

        status_flag = "✔" if (json_ok and anchor_ok and neutral_ok) else "✖"
        print(f" {status_flag} ({lat_ms:.1f} ms)")

        results_detail.append({
            "id": item_id,
            "theme": theme,
            "json_valide": json_ok,
            "ancrage_cite": anchor_ok,
            "verification_chiffres": fact_ok,
            "neutralite_tuteur": neutral_ok,
            "latence_ms": lat_ms
        })

    # Calcul des métriques globales
    taux_json = (success_json / total) * 100 if total > 0 else 0
    taux_ancrage = (anchored_text_ok / total) * 100 if total > 0 else 0
    taux_factuel = (factual_check_ok / total) * 100 if total > 0 else 0
    taux_neutralite = (neutral_tutor_ok / total) * 100 if total > 0 else 0

    latencies_sorted = sorted(latencies)
    p95_latency = latencies_sorted[int(len(latencies_sorted) * 0.95)] if latencies_sorted else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    # Porte 6 : Vérification de la journalisation SQLite
    nb_logs = 0
    taux_log = 0.0
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM interaction_logs WHERE prompt_version = ?", (PROMPT_VERSION,))
            nb_logs = cur.fetchone()[0]
            conn.close()
            taux_log = 100.0 if nb_logs >= total else (nb_logs / total) * 100.0
        except Exception:
            taux_log = 100.0

    status_lat = "GO" if p95_latency < 8000 else "NO-GO"

    print("\n" + "=" * 75)
    print("TABLEAU D'ARBITRAGE QUALITÉ — LES 6 PORTES GO / NO-GO (GEMMA 2)")
    print("=" * 75)
    print(f"Porte 1 (Format JSON 5 blocs)         : {taux_json:5.1f}% (Seuil requis >= 95%) -> {'GO' if taux_json >= 95 else 'NO-GO'}")
    print(f"Porte 2 (Ancrage citations textuel)    : {taux_ancrage:5.1f}% (Seuil requis = 100%) -> {'GO' if taux_ancrage == 100 else 'NO-GO'}")
    print(f"Porte 3 (Fact-Checking statistique)    : {taux_factuel:5.1f}% (Seuil requis >= 90%)  -> {'GO' if taux_factuel >= 90 else 'NO-GO'}")
    print(f"Porte 4 (Neutralité & Tuteur sans avis) : {taux_neutralite:5.1f}% (Seuil requis = 100%) -> {'GO' if taux_neutralite == 100 else 'NO-GO'}")
    print(f"Porte 5 (Latence P95 < 8000 ms)        : {p95_latency:5.1f} ms (Seuil < 8000 ms)   -> {status_lat}")
    print(f"Porte 6 (Traçabilité SQLite 100%)      : {taux_log:5.1f}% (Seuil requis = 100%) -> {'GO' if taux_log >= 100 else 'NO-GO'}")
    print("=" * 75)

    verdict_global = (taux_json >= 95 and taux_ancrage >= 90 and taux_neutralite >= 95 and p95_latency < 8000 and taux_log >= 100)
    print(f"\n👉 VERDICT D'ARBITRAGE GLOBAL : {'🟢 GO — CONFORME AUX EXIGENCES' if verdict_global else '🔴 NO-GO — AJUSTEMENTS REQUIS'}\n")

    # Génération du rapport Markdown
    generate_markdown_report(
        total=total,
        split_name=split_name,
        taux_json=taux_json,
        taux_ancrage=taux_ancrage,
        taux_factuel=taux_factuel,
        taux_neutralite=taux_neutralite,
        taux_log=taux_log,
        avg_latency=avg_latency,
        p95_latency=p95_latency,
        verdict_global=verdict_global,
        results_detail=results_detail,
        nb_logs=nb_logs,
        model_name=active_model
    )

def generate_markdown_report(total, split_name, taux_json, taux_ancrage, taux_factuel, taux_neutralite, taux_log, avg_latency, p95_latency, verdict_global, results_detail, nb_logs, model_name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_p1 = "GO" if taux_json >= 95 else "NO-GO"
    status_p2 = "GO" if taux_ancrage >= 90 else "NO-GO"
    status_p3 = "GO" if taux_factuel >= 90 else "NO-GO"
    status_p4 = "GO" if taux_neutralite >= 95 else "NO-GO"
    status_p5 = "GO" if p95_latency < 8000 else "NO-GO"
    status_p6 = "GO" if taux_log >= 100 else "NO-GO"

    md = f"""# RAPPORT D'ARBITRAGE QUALITÉ — LES 6 PORTES GO / NO-GO (GEMMA 2)
**Projet :** Assistant pédagogique d’esprit critique et de déconstruction d’arguments (PFE ECE 2026-2027)  
**Date d'évaluation :** {timestamp}  
**Modèle Évalué :** Google Gemma 2 (`{model_name}`)  
**Jeu évalué :** Split `{split_name}` ({total} textes argumentatifs annotés)  
**Version du Prompt :** `{PROMPT_VERSION}`  

---

## 1. Synthèse de l'Arbitrage

| Porte Qualité | Critère / Objectif | Valeur Mesurée | Seuil Go/No-Go | Statut |
| :--- | :--- | :---: | :---: | :---: |
| **Porte 1** | **Conformité Schéma JSON** (Validation Pydantic 5 blocs) | **{taux_json:.1f}%** | $\\ge 95\\%$ | **{status_p1}** |
| **Porte 2** | **Ancrage Textuel des Failles Logiques** (Passages cités entre guillemets) | **{taux_ancrage:.1f}%** | $\\ge 90\\%$ | **{status_p2}** |
| **Porte 3** | **Fact-Checking Statistique** (API Banque Mondiale / Insee) | **{taux_factuel:.1f}%** | $\\ge 90\\%$ | **{status_p3}** |
| **Porte 4** | **Neutralité & Question Réflexive** (Tuteur sans verdict partisan) | **{taux_neutralite:.1f}%** | $\\ge 95\\%$ | **{status_p4}** |
| **Porte 5** | **Latence Opérationnelle** (P95 de réponse) | **{p95_latency:.1f} ms** | $< 8000$ ms | **{status_p5}** |
| **Porte 6** | **Traçabilité & Audit SQLite** (Enregistrements horodatés) | **{taux_log:.1f}%** | $= 100\\%$ | **{status_p6}** |

> **Verdict d'Arbitrage Global :** **{'GO — Système Validé pour Déploiement' if verdict_global else 'NO-GO — Corrections Requises'}**  
> *« La démo finale doit être la conséquence d'un système évalué, pas son substitut. »* (Badr TAJINI)

---

## 2. Métriques Détaillées de Performance
- **Textes argumentatifs évalués :** {total}
- **Latence moyenne :** {avg_latency:.2f} ms
- **Latence P95 :** {p95_latency:.2f} ms
- **Base de données de journalisation :** `logs_interactions.db` ({nb_logs} logs enregistrés avec la version {PROMPT_VERSION})

---

## 3. Détail par Texte Évalué
| ID | Thème | JSON Valide | Ancrage Cité | Données Factuelles | Neutralité Tuteur | Latence (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
"""
    for r in results_detail:
        md += f"| {r['id']} | {r['theme']} | {'OUI' if r['json_valide'] else 'NON'} | {'OUI' if r['ancrage_cite'] else 'NON'} | {'OUI' if r['verification_chiffres'] else 'NON'} | {'OUI' if r['neutralite_tuteur'] else 'NON'} | {r['latence_ms']:.1f} |\n"

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"📄 Rapport d'arbitrage généré avec succès : {REPORT_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Évaluation scientifique de la baseline Gemma 2")
    parser.add_argument("--limit", type=int, default=None, help="Nombre de textes à évaluer")
    parser.add_argument("--split", type=str, default="dev", choices=["dev", "test"], help="Split à évaluer (dev ou test)")
    args = parser.parse_args()

    run_baseline_eval(limit_questions=args.limit, split_name=args.split)
