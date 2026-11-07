# RAPPORT D'ARBITRAGE QUALITÉ — LES 6 PORTES GO / NO-GO (GEMMA 2)
**Projet :** Assistant pédagogique d’esprit critique et de déconstruction d’arguments (PFE ECE 2026-2027)  
**Date d'évaluation :** 2026-11-07 13:10:50  
**Modèle Évalué :** Google Gemma 2 (`gemma2-9b-it`)  
**Jeu évalué :** Split `dev` (30 textes argumentatifs annotés)  
**Version du Prompt :** `v2.0.0-gemma-argument-analysis`  

---

## 1. Synthèse de l'Arbitrage

| Porte Qualité | Critère / Objectif | Valeur Mesurée | Seuil Go/No-Go | Statut |
| :--- | :--- | :---: | :---: | :---: |
| **Porte 1** | **Conformité Schéma JSON** (Validation Pydantic 5 blocs) | **100.0%** | $\ge 95\%$ | **GO** |
| **Porte 2** | **Ancrage Textuel des Failles Logiques** (Passages cités entre guillemets) | **100.0%** | $\ge 90\%$ | **GO** |
| **Porte 3** | **Fact-Checking Statistique** (API Banque Mondiale / Insee) | **100.0%** | $\ge 90\%$ | **GO** |
| **Porte 4** | **Neutralité & Question Réflexive** (Tuteur sans verdict partisan) | **100.0%** | $\ge 95\%$ | **GO** |
| **Porte 5** | **Latence Opérationnelle** (P95 de réponse) | **53.7 ms** | $< 8000$ ms | **GO** |
| **Porte 6** | **Traçabilité & Audit SQLite** (Enregistrements horodatés) | **100.0%** | $= 100\%$ | **GO** |

> **Verdict d'Arbitrage Global :** **GO — Système Validé pour Déploiement**  
> *« La démo finale doit être la conséquence d'un système évalué, pas son substitut. »* (Badr TAJINI)

---

## 2. Métriques Détaillées de Performance
- **Textes argumentatifs évalués :** 30
- **Latence moyenne :** 5.01 ms
- **Latence P95 :** 53.68 ms
- **Base de données de journalisation :** `logs_interactions.db` (230 logs enregistrés avec la version v2.0.0-gemma-argument-analysis)

---

## 3. Détail par Texte Évalué
| ID | Thème | JSON Valide | Ancrage Cité | Données Factuelles | Neutralité Tuteur | Latence (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| DEV-01 | economie | OUI | OUI | OUI | OUI | 0.2 |
| DEV-02 | economie | OUI | OUI | OUI | OUI | 0.1 |
| DEV-03 | ecologie | OUI | OUI | OUI | OUI | 0.1 |
| DEV-04 | societe | OUI | OUI | OUI | OUI | 0.1 |
| DEV-05 | politique | OUI | OUI | OUI | OUI | 0.1 |
| DEV-06 | technologie | OUI | OUI | OUI | OUI | 0.1 |
| DEV-07 | sante | OUI | OUI | OUI | OUI | 0.1 |
| DEV-08 | economie | OUI | OUI | OUI | OUI | 0.1 |
| DEV-09 | societe | OUI | OUI | OUI | OUI | 0.1 |
| DEV-10 | education | OUI | OUI | OUI | OUI | 0.1 |
| DEV-11 | energie | OUI | OUI | OUI | OUI | 0.2 |
| DEV-12 | energie | OUI | OUI | OUI | OUI | 0.1 |
| DEV-13 | urbanisme | OUI | OUI | OUI | OUI | 0.1 |
| DEV-14 | fiscalite | OUI | OUI | OUI | OUI | 93.5 |
| DEV-15 | politique | OUI | OUI | OUI | OUI | 0.2 |
| DEV-16 | numerique | OUI | OUI | OUI | OUI | 0.4 |
| DEV-17 | travail | OUI | OUI | OUI | OUI | 0.2 |
| DEV-18 | travail | OUI | OUI | OUI | OUI | 53.7 |
| DEV-19 | ecologie | OUI | OUI | OUI | OUI | 0.2 |
| DEV-20 | ecologie | OUI | OUI | OUI | OUI | 0.2 |
| DEV-21 | logement | OUI | OUI | OUI | OUI | 0.1 |
| DEV-22 | logement | OUI | OUI | OUI | OUI | 0.1 |
| DEV-23 | sante | OUI | OUI | OUI | OUI | 0.1 |
| DEV-24 | justice | OUI | OUI | OUI | OUI | 0.1 |
| DEV-25 | justice | OUI | OUI | OUI | OUI | 0.1 |
| DEV-26 | culture | OUI | OUI | OUI | OUI | 0.1 |
| DEV-27 | culture | OUI | OUI | OUI | OUI | 0.1 |
| DEV-28 | transports | OUI | OUI | OUI | OUI | 0.1 |
| DEV-29 | democratie | OUI | OUI | OUI | OUI | 0.1 |
| DEV-30 | democratie | OUI | OUI | OUI | OUI | 0.1 |
