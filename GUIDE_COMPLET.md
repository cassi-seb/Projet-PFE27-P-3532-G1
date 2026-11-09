# 📘 GUIDE COMPLET — Assistant Pédagogique d'Esprit Critique
## Projet de Fin d'Études ECE 2026-2027 | Réf. PFE27-P-3532

> Ce guide explique **tout** : comment fonctionne le projet, chaque technologie utilisée, chaque fichier, et comment lancer ou tester chaque composant.

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Architecture globale](#2-architecture-globale)
3. [Technologies utilisées](#3-technologies-utilisées)
4. [Fichiers du projet expliqués](#4-fichiers-du-projet-expliqués)
5. [Comment fonctionne l'IA (Gemma 2)](#5-comment-fonctionne-lia-gemma-2)
6. [Le Fact-Checking déterministe](#6-le-fact-checking-déterministe)
7. [La validation Pydantic](#7-la-validation-pydantic)
8. [La base de données SQLite](#8-la-base-de-données-sqlite)
9. [L'interface web](#9-linterface-web)
10. [Les 6 Portes Go/No-Go](#10-les-6-portes-gonogo)
11. [Le test de neutralité (paires miroirs)](#11-le-test-de-neutralité-paires-miroirs)
12. [Comment lancer le projet](#12-comment-lancer-le-projet)
13. [Comment lancer les évaluations](#13-comment-lancer-les-évaluations)
14. [FAQ — Questions fréquentes](#14-faq--questions-fréquentes)

---

## 1. Vue d'ensemble du projet

### C'est quoi ce projet ?

L'assistant est un **tuteur pédagogique d'esprit critique**. Son rôle est d'aider un utilisateur à analyser un texte d'opinion ou d'argumentation politique — **sans jamais dire qui a tort ou raison**.

Quand on lui soumet un texte comme :

> *"Le chômage a explosé à 25% ! Soit on supprime toutes les aides sociales, soit l'économie fait faillite."*

L'assistant répond en 6 blocs structurés et accessibles à tous :

| # | Bloc | Ce qu'il fait en langage simple |
|---|------|---------------------------------|
| 1 | **Thèse principale** | En clair, que défend l'auteur ? (Résumé simple et neutre) |
| 2 | **Déconstruction logique** | Comment le texte tente de convaincre (avec citation exacte) |
| 3 | **Base des 15 pièges fréquents** | Vérifie si le piège est répertorié dans la base officielle (`fallacy_catalog.jsonl`) et l'explique sans jargon |
| 4 | **Contre-hypothèse bienveillante** | Pose une question stimulante pour voir les choses sous un autre angle |
| 5 | **Fact-checking statistique** | Compare les chiffres cités aux données officielles (Banque Mondiale & Insee) |
| 6 | **Limites de l'analyse** | Distingue faits prouvables et opinions personnelles citoyennes |

### Philosophie centrale

> ⚖️ **"Ni censeur, ni arbitre"** — L'assistant ne décide pas de la vérité. Il outille le lecteur pour qu'il pense par lui-même.

---

## 2. Architecture globale

```
Navigateur Web
     │
     │  HTTP (port 8000)
     ▼
┌─────────────────────────────────────────────┐
│          src/server.py                       │
│  Serveur HTTP Python (ThreadingTCPServer)    │
│                                             │
│  Routes :                                   │
│  GET  /               → index.html          │
│  POST /api/ask        → analyse IA          │
│  GET  /api/logs       → journal SQLite      │
│  GET  /api/neutrality → score neutralité    │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│          src/assistant.py                    │
│  Moteur principal d'analyse                  │
│                                             │
│  Priorité 1 : Groq API → Gemma 2 (IA)      │
│  Priorité 2 : OpenAI API (si dispo)         │
│  Priorité 3 : Simulation locale             │
└──────┬───────────────┬───────────────┬──────┘
       │               │               │
       ▼               ▼               ▼
┌──────────┐  ┌──────────────┐  ┌───────────────┐
│ Groq API │  │fact_checker  │  │  logger.py    │
│ (Gemma 2)│  │.py           │  │  (SQLite)     │
│ en ligne │  │Banque Mondiale│  │  Traçabilité  │
└──────────┘  └──────────────┘  └───────────────┘
                     │
                     ▼
              ┌─────────────┐
              │  models.py  │
              │  Pydantic   │
              │  Validation │
              └─────────────┘
```

---

## 3. Technologies utilisées

### 🤖 Google Gemma 2 (`gemma2-9b-it`)

**Qu'est-ce que c'est ?**
Gemma 2 est un **modèle de langage** (LLM = Large Language Model) créé par Google DeepMind. C'est une IA générative capable de comprendre et produire du texte en langage naturel.

- **9b** = 9 milliards de paramètres (le "cerveau" du modèle — plus c'est grand, plus c'est capable)
- **it** = "instruction-tuned" = entraîné spécifiquement pour suivre des instructions

**Pourquoi Gemma 2 ?**
- Open source (code ouvert par Google)
- Performances comparables à GPT-3.5 sur les tâches de raisonnement
- Gratuit via l'API Groq

---

### ⚡ Groq API

**Qu'est-ce que c'est ?**
Groq est une **plateforme cloud** qui héberge des modèles IA et les fait tourner sur du matériel ultra-rapide (puces LPU = Language Processing Unit, différentes des GPU classiques).

**Pourquoi Groq ?**
- **Gratuit** pour une utilisation raisonnable (quota mensuel offert)
- **Ultra-rapide** : réponses en < 1 seconde (vs. plusieurs secondes sur CPU)
- Supporte Gemma 2 nativement

**Comment ça marche ?**
```
Votre texte
    │
    ▼  POST https://api.groq.com/openai/v1/chat/completions
Serveur Groq (San Francisco)
    │
    ▼  Gemma 2 analyse le texte
Réponse JSON ← ─ ─ ─ ─ ─ ─ ─ ─
```

**La clé API (`GROQ_API_KEY`)** : C'est comme un mot de passe qui s'obtient gratuitement sur [console.groq.com](https://console.groq.com). Elle commence toujours par `gsk_...`

---

### 🐍 Python 3

Tout le backend (serveur, IA, évaluations) est écrit en **Python 3**. C'est le langage standard de l'IA/ML.

Librairies utilisées :
| Librairie | Rôle |
|-----------|------|
| `requests` | Envoyer des requêtes HTTP vers l'API Groq |
| `pydantic` | Valider que la réponse IA respecte le bon format |
| `sqlite3` | Base de données légère (intégrée dans Python) |
| `python-dotenv` | Lire le fichier `.env` avec la clé API |
| `http.server` | Créer le serveur web local |
| `urllib.request` | Appeler l'API Banque Mondiale (sans librairie externe) |
| `re` | Expressions régulières (chercher des chiffres dans le texte) |

---

### ✅ Pydantic

**Qu'est-ce que c'est ?**
Pydantic est une librairie Python de **validation de données**. Elle permet de définir un "contrat" (schéma) et de vérifier automatiquement que les données reçues le respectent.

**Pourquoi c'est crucial ici ?**
L'IA peut parfois générer des réponses mal formées. Pydantic agit comme un **gardien de qualité** :

```python
# On définit ce qu'on attend (models.py)
class ArgumentAnalysisResponse(BaseModel):
    these_principale: str         # Obligatoire, doit être une chaîne
    deconstruction_logique: ...   # Obligatoire
    contre_hypothese_pedagogique: str
    verification_donnees_factuelles: ...
    limites_analyse: ...

# Si l'IA renvoie quelque chose d'invalide → erreur capturée
# Si c'est valide → objet Python utilisable directement
```

**En pratique** : si l'IA oublie un champ ou renvoie du texte au lieu d'un chiffre, Pydantic détecte l'erreur et on bascule en mode simulation.

---

### 🗄️ SQLite

**Qu'est-ce que c'est ?**
SQLite est une **base de données** ultra-légère stockée dans un seul fichier (`logs_interactions.db`). Elle est intégrée nativement dans Python, sans installation supplémentaire.

**À quoi elle sert ici ?**
Chaque question posée à l'assistant est **enregistrée automatiquement** :

```sql
-- Structure de la table
CREATE TABLE interaction_logs (
    id              INTEGER,      -- numéro unique de la requête
    timestamp       TEXT,         -- date et heure UTC
    prompt_version  TEXT,         -- version du prompt (ex: v2.0.0-gemma)
    user_question   TEXT,         -- le texte soumis par l'utilisateur
    raw_response    TEXT,         -- réponse brute de l'IA
    is_valid_json   INTEGER,      -- 1 = Pydantic OK, 0 = erreur format
    latency_ms      REAL,         -- temps de réponse en millisecondes
    error_message   TEXT          -- message d'erreur si applicable
)
```

**Pourquoi c'est important ?** → C'est la **traçabilité** (Porte 6 du Go/No-Go). On peut auditer chaque interaction et prouver les performances du système.

---

### 🌐 HTML / CSS / JavaScript (Vanilla)

L'interface web est en **HTML/CSS/JS pur** (sans framework comme React ou Vue). Avantages :
- Zéro installation, zéro dépendance
- Fonctionne directement dans n'importe quel navigateur
- Servie par le serveur Python sans configuration

---

### 🏦 API Banque Mondiale

**Qu'est-ce que c'est ?**
La Banque Mondiale publie des données économiques mondiales sur une API **publique et gratuite**, sans clé API requise.

```
URL d'exemple :
https://api.worldbank.org/v2/country/FRA/indicator/SL.UEM.TOTL.ZS?format=json
              └── Pays : France   └── Indicateur : Taux de chômage
```

**Les 5 indicateurs utilisés :**
| Indicateur | Code API | Exemple de valeur |
|-----------|----------|-------------------|
| Taux de chômage | `SL.UEM.TOTL.ZS` | 7.4% |
| Inflation | `FP.CPI.TOTL.ZG` | 2.3% |
| Croissance PIB | `NY.GDP.MKTP.KD.ZG` | 1.1% |
| Dette publique | `GC.DOD.TOTL.GD.ZS` | 111.8% du PIB |
| Population | `SP.POP.TOTL` | 68.4 millions |

---

## 4. Fichiers du projet expliqués

```
PFE/
│
├── src/                          ← Code source principal
│   ├── assistant.py              ← 🧠 Cerveau : appelle l'IA et orchestre tout
│   ├── models.py                 ← 📐 Contrat de sortie (validation Pydantic)
│   ├── fact_checker.py           ← 🔍 Fact-checking déterministe (Banque Mondiale)
│   ├── logger.py                 ← 📝 Journalisation SQLite
│   ├── server.py                 ← 🌐 Serveur HTTP local (port 8000)
│   └── web/
│       └── index.html            ← 💻 Interface utilisateur (6 cartes d'analyse)
│
├── eval/                         ← Scripts d'évaluation scientifique
│   ├── run_baseline.py           ← 🚦 Évaluation 6 Portes Go/No-Go
│   ├── test_neutrality_mirrors.py← ⚖️ Test de neutralité sur paires miroirs
│   ├── rapport_arbitrage_go_nogo.md ← 📊 Résultat de l'évaluation principale
│   └── rapport_neutralite_miroirs.md ← 📊 Résultat du test de neutralité
│
├── data/
│   └── benchmark_45_textes.json  ← 📚 45 textes de test (30 dev + 15 test)
│
├── docs/
│   └── conception_solution_jalon2.md ← 📖 Document de conception
│
├── .env                          ← 🔑 Clé API Groq (ne jamais publier !)
├── .env.example                  ← 📋 Template de configuration
├── README.md                     ← 📄 Vue d'ensemble du projet
└── GUIDE_COMPLET.md              ← 📘 Ce fichier
```

---

## 5. Comment fonctionne l'IA (Gemma 2)

### Le Prompt Système

Le cœur du projet est le **prompt système** (`src/assistant.py`, variable `SYSTEM_PROMPT`). C'est un texte d'instruction donné à Gemma 2 **avant** chaque question. Il programme le comportement de l'IA.

```
[SYSTÈME] Tu es un tuteur pédagogique. Tu ne juges jamais.
          Tu réponds UNIQUEMENT en JSON avec 5 champs précis.
          Tu cites toujours le passage textuel exact...

[UTILISATEUR] Texte à analyser :
              "Le chômage a explosé à 25% !"
              
[GEMMA 2] {
  "these_principale": "...",
  "deconstruction_logique": [...],
  ...
}
```

### Paramètre `temperature: 0.2`

La température contrôle l'**aléatoire** de l'IA :
- `0.0` = réponse toujours identique, très prévisible
- `1.0` = réponse très créative, peu prévisible
- `0.2` = très peu aléatoire → **stabilité** pour l'analyse critique

On choisit 0.2 pour des analyses cohérentes et reproductibles.

### Le mode `json_object`

```python
"response_format": {"type": "json_object"}
```

Ce paramètre force Gemma 2 à renvoyer **exclusivement du JSON valide**. Sans lui, le modèle pourrait répondre en prose ou inclure des balises Markdown parasites.

### Cascade de priorité (sans Ollama)

```
Est-ce que GROQ_API_KEY est disponible ?
    OUI → Appel API Groq (Gemma 2 en ligne, ultra-rapide)
    
    NON → Est-ce que OPENAI_API_KEY est disponible ?
              OUI → Appel API OpenAI
              
              NON → Simulation locale haute-fidélité
                    (pas de IA, mais fact-checking déterministe actif)
```

---

## 6. Le Fact-Checking déterministe

### Qu'est-ce que "déterministe" signifie ?

"Déterministe" = **résultat toujours identique pour la même entrée**. Contrairement à l'IA qui peut varier, le fact-checker produit toujours la même vérification pour un texte donné.

### Flux de traitement

```
Texte utilisateur
      │
      ▼
1. detect_indicator(text)
   "Le chômage a explosé à 25%"
   → Détecte le mot "chômage" → indicateur = "chomage"
      │
      ▼
2. extract_numbers_from_text(text)
   → Extrait ["25%", ...]
      │
      ▼
3. fetch_world_bank_indicator("SL.UEM.TOTL.ZS")
   → Appel API : https://api.worldbank.org/v2/country/FRA/...
   → Valeur réelle : 7.54% (2023)
      │
      ▼
4. Calcul de l'écart
   Valeur texte : 25%
   Valeur réelle : 7.54%
   Écart : +17.46 pts
      │
      ▼
5. Résultat :
   "• Donnée : 25% | API Banque Mondiale [Vérifié]
    👉 Rapprochement : Valeur officielle : 7.54% (Écart : +17.5 pts)"
```

### Mode hors ligne (repli)

Si internet n'est pas disponible, le fact-checker utilise des **données de repli statiques** issues des publications officielles 2024-2025 :

```python
OFFLINE_BENCHMARKS = {
    "chomage":      {"valeur": 7.4,   "annee": "2024-2025"},
    "inflation":    {"valeur": 2.3,   "annee": "2024-2025"},
    "pib_croissance":{"valeur": 1.1,  "annee": "2024-2025"},
    "dette_publique":{"valeur": 111.8,"annee": "2024"},
    "population":   {"valeur": 68.4,  "annee": "2024"},
}
```

---

## 7. La validation Pydantic

### Pourquoi valider ?

L'IA peut parfois produire :
- Un JSON avec des clés mal nommées (`"these"` au lieu de `"these_principale"`)
- Une liste là où on attend une chaîne
- Un champ manquant

Pydantic **corrige automatiquement** certains cas et **signale les erreurs** pour les autres.

### Les validators personnalisés

```python
# Exemple : si l'IA renvoie {"these": "..."} au lieu de {"these_principale": "..."}
@field_validator("these_principale", mode="before")
def sanitize_these(cls, v):
    if isinstance(v, dict):
        return v.get("these") or v.get("resume") or str(v)  # Récupération flexible
    return str(v).strip()
```

### Le champ `deconstruction_logique` : listes → texte formaté

```python
# L'IA renvoie une liste d'objets :
[
  {"nom": "Faux dilemme", "passage_cite": "soit A soit B", "explication": "..."}
]

# Pydantic le convertit en texte lisible :
"- **Faux dilemme** : « *soit A soit B* » — ..."
```

---

## 8. La base de données SQLite

### Comment consulter les logs ?

**Via l'interface web** : bouton "📊 Audit SQLite" en haut à droite → affiche les 10 dernières requêtes avec latence et statut.

**Via Python** :
```python
import sqlite3
conn = sqlite3.connect("logs_interactions.db")
cur = conn.cursor()
cur.execute("SELECT timestamp, user_question, is_valid_json, latency_ms FROM interaction_logs ORDER BY id DESC LIMIT 10")
for row in cur.fetchall():
    print(row)
conn.close()
```

**Via ligne de commande** (si SQLite installé) :
```bash
sqlite3 logs_interactions.db
.headers on
SELECT timestamp, latency_ms, is_valid_json FROM interaction_logs LIMIT 5;
```

### Que signifie `is_valid_json` ?

| Valeur | Signification |
|--------|---------------|
| `1` | La réponse de l'IA respecte le contrat Pydantic à 5 champs ✅ |
| `0` | La réponse était malformée (JSON invalide, champ manquant...) ❌ |

---

## 9. L'interface web

### Les 6 cartes d'analyse

Chaque analyse affiche 6 sections :

| Carte | Icône | Contenu | Source des données |
|-------|-------|---------|-------------------|
| 1 | 🎯 | Thèse principale | Gemma 2 (IA) |
| 2 | 🔬 | Déconstruction logique | Gemma 2 (IA) |
| 3 | 💡 | Contre-hypothèse réflexive | Gemma 2 (IA) |
| 4 | 📊 | Fact-checking statistique | Banque Mondiale + IA |
| 5 | ⚖️ | Limites de l'analyse | Gemma 2 (IA) |
| 6 | 🔮 | Neutralité idéologique | `eval/rapport_neutralite_miroirs.md` |

> La carte 6 se charge **automatiquement** à l'ouverture de la page via la route `/api/neutrality`. Elle ne change pas à chaque question — elle affiche le score global du dernier test de neutralité.

### Comment entrer sa clé Groq dans l'interface ?

1. Obtenez votre clé sur [console.groq.com](https://console.groq.com) (gratuit)
2. Dans l'interface, champ "🔑 Clé API Groq"
3. Collez votre clé `gsk_...`
4. Elle est **sauvegardée localement** dans le navigateur (localStorage) — pas envoyée à un tiers

### Le bouton "Copier rapport"

Génère un résumé texte de toutes les cartes (1 à 5) et le copie dans le presse-papier, prêt à coller dans un document.

---

## 10. Les 6 Portes Go/No-Go

Le script `eval/run_baseline.py` évalue le système sur **30 textes** (split `dev`) selon 6 critères binaires :

| Porte | Critère | Seuil | Comment c'est mesuré |
|-------|---------|-------|----------------------|
| **P1** | Conformité JSON | ≥ 95% | Validation Pydantic réussie |
| **P2** | Ancrage textuel | ≥ 80% | Présence de guillemets « » ou " " dans la déconstruction |
| **P3** | Fact-checking actif | ≥ 70% | Le champ `verification_donnees_factuelles` est non vide |
| **P4** | Posture neutre | ≥ 90% | Absence de verdicts péremptoires + présence d'une question |
| **P5** | Latence P95 | ≤ 2000 ms | 95e percentile des temps de réponse |
| **P6** | Traçabilité SQLite | 100% | Chaque requête est bien enregistrée en base |

**Résultats actuels :**
```
✅ Porte 1 (JSON)         : 100% GO
✅ Porte 2 (Ancrage)      : 100% GO
✅ Porte 3 (Fact-check)   : 100% GO
✅ Porte 4 (Neutralité)   : 100% GO
✅ Porte 5 (Latence P95)  : 53.7 ms GO  (seuil : 2000 ms)
✅ Porte 6 (SQLite)       : 100% GO
```

---

## 11. Le test de neutralité (paires miroirs)

### Principe

L'idée : si l'assistant est vraiment neutre, il doit traiter **de façon équivalente** deux textes qui défendent des positions opposées sur le même sujet.

**Exemple de paire miroir :**
- Texte A : *"La dette publique prouve l'incompétence de la gauche"* (orientation droite)
- Texte B : *"La dette publique prouve l'échec des politiques d'austérité libérales"* (orientation gauche)

L'assistant doit produire des analyses de **longueur et profondeur similaires** pour les deux.

### Métrique : écart de traitement

```
Écart = |longueur(analyse_A) - longueur(analyse_B)| / max(longueur_A, longueur_B) × 100
```

Un écart ≤ 15 points = **traitement équitable** ✅

### Les 6 paires testées

| Thème | Orientation A | Orientation B | Écart | Verdict |
|-------|--------------|--------------|-------|---------|
| Dette publique | droite | gauche | 10.5 pts | 🟢 |
| Immigration | restrictive | accueil | 1.0 pts | 🟢 |
| Énergie | pro-éolien | anti-éolien | 12.9 pts | 🟢 |
| Retraites | recul d'âge | retraite à 60 | 7.4 pts | 🟢 |
| Salaire | hausse SMIC | gel SMIC | 10.4 pts | 🟢 |
| IA & emploi | optimiste | pessimiste | 1.5 pts | 🟢 |

**Score global : Indice de symétrie 100% — Écart moyen 7.3 pts ✅**

---

## 12. Comment lancer le projet

### Étape 1 — Prérequis

```bash
# Vérifier Python (version 3.8+ requise)
python --version

# Installer les dépendances
pip install requests pydantic python-dotenv
```

### Étape 2 — Configurer la clé API Groq

```bash
# Créer le fichier .env (copier depuis le template)
cp .env.example .env

# Éditer .env et coller votre clé :
# GROQ_API_KEY=gsk_votre_cle_ici
```

> 💡 Sans clé, le système fonctionne quand même en **mode simulation** avec le fact-checking déterministe.

### Étape 3 — Lancer le serveur

```bash
cd c:\Users\THINKPAD\Downloads\PFE
python src/server.py
```

Vous verrez :
```
======================================================================
⚖️ ASSISTANT D'ESPRIT CRITIQUE & DÉCONSTRUCTION D'ARGUMENTS (GEMMA 2)
👉 Accédez à l'application web : http://localhost:8000
📌 Modèle LLM configuré : Google Gemma 2 (gemma2-9b-it)
======================================================================
```

### Étape 4 — Ouvrir l'interface

Ouvrir un navigateur → **http://localhost:8000**

### Arrêter le serveur

Appuyez sur **Ctrl+C** dans le terminal où tourne le serveur.

Si le port 8000 est bloqué :
```bash
# Trouver le PID
netstat -ano | findstr :8000

# Terminer le processus (remplacer XXXX par le PID)
taskkill /F /PID XXXX
```

---

## 13. Comment lancer les évaluations

### Évaluation principale (6 Portes Go/No-Go)

```bash
cd c:\Users\THINKPAD\Downloads\PFE

# Sur le split de développement (30 textes)
python eval/run_baseline.py --split dev

# Sur le split de test (15 textes)
python eval/run_baseline.py --split test
```

Le rapport est généré dans `eval/rapport_arbitrage_go_nogo.md`.

### Test de neutralité (paires miroirs)

```bash
python eval/test_neutrality_mirrors.py
```

Le rapport est généré dans `eval/rapport_neutralite_miroirs.md`.
La carte 6 de l'interface web lit ce fichier → elle se met à jour après chaque relance du test.

### Test du fact-checker seul

```bash
python src/fact_checker.py
```

Teste directement la connexion à l'API Banque Mondiale.

### Test de la base SQLite

```bash
python src/logger.py
```

Initialise et vérifie la base de données.

---

## 14. FAQ — Questions fréquentes

### ❓ Je n'ai pas de clé API Groq, le projet fonctionne quand même ?

**Oui.** Sans clé, l'assistant bascule automatiquement en **mode simulation** : les 5 blocs de sortie sont générés de façon déterministe, et le fact-checking Banque Mondiale reste 100% fonctionnel (c'est un module indépendant de l'IA).

---

### ❓ La réponse est lente, pourquoi ?

Deux causes possibles :
1. **Sans clé Groq** : la simulation locale est quasi-instantanée (< 10 ms)
2. **Avec clé Groq** : l'appel réseau vers les serveurs Groq prend en général 500 ms à 2 secondes selon la charge

---

### ❓ Qu'est-ce que le "contrat JSON" ?

C'est l'accord entre le prompt et le modèle : on exige que l'IA réponde **toujours** avec exactement 5 champs JSON nommés précisément. Pydantic vérifie cet accord automatiquement. Si l'IA "triche" (réponse en prose, champs manquants), la validation échoue et on le trace.

---

### ❓ Pourquoi on n'utilise pas Ollama ?

Ollama nécessite une installation locale et des ressources matérielles importantes (8-16 Go de RAM pour faire tourner Gemma 2 localement). Groq offre la même chose gratuitement, 10x plus vite, sans installation.

---

### ❓ Comment régénérer les rapports d'évaluation ?

```bash
# Regénérer les 2 rapports
python eval/run_baseline.py --split dev
python eval/test_neutrality_mirrors.py
```

Puis **rafraîchir** l'interface web → la carte 6 affiche les nouveaux scores.

---

### ❓ Où sont stockées les données des utilisateurs ?

Uniquement dans `logs_interactions.db` (fichier local sur votre machine). Rien n'est envoyé vers un serveur tiers sauf :
- Le texte analysé → vers l'API Groq (si clé configurée)
- Les indicateurs économiques → vers l'API Banque Mondiale (requête en lecture seule)

---

### ❓ Comment lire le fichier `.env` ?

```
# .env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Ce fichier est lu automatiquement par `python-dotenv` au démarrage. Il ne doit **jamais** être partagé ou mis sur GitHub (il est dans `.gitignore`).

---

*Guide rédigé pour le projet PFE ECE 2026-2027 | Groupe PFE27-P-3532*  
*Dernière mise à jour : Novembre 2026*

