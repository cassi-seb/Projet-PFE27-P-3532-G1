# 🎓 Portfolio PFE — Assistant Pédagogique d'Esprit Critique et de Déconstruction d'Arguments

**Projet de Fin d’Études ECE 2026-2027 — Catégorie Produit**  
**Équipe :** Aurelien Jacson (*Create*), Bryan Tachi Yemelong (*Data & IA*), Suzy Cassandra Ebobisse (*Data & IA*), Timothée Wyrzykowski (*Finance*), Yassir Mousmahi (*Cybersécurité*)  
**Coach référent :** Badr TAJINI  
**Moteur d'inférence central :** **Google Gemma 2** (`gemma2-9b-it` via API Groq ultra-rapide)  
**Version du document :** Version consolidée — Transition Gemma 2 & Sujet Esprit Critique  

---

## 🚀 Démarrage Rapide (En 3 Minutes)

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Modèle Google Gemma 2 (Ultra-rapide & 100% Gratuit via Groq)
Le modèle **Google Gemma 2 9B** (`gemma2-9b-it`) est exécuté via **Groq** (temps de réponse < 1 seconde, aucune installation lourde sur le PC) :
* Obtenez votre clé gratuite en 30 secondes sur **[console.groq.com/keys](https://console.groq.com/keys)**
* Deux manières d'activer votre clé :
  - **Option A :** Collez-la directement dans le champ *« Clé Groq »* en haut de l'interface web (enregistrée dans votre navigateur).
  - **Option B :** Créez un fichier `.env` à la racine contenant :
    ```env
    GROQ_API_KEY=gsk_votre_cle_ici
    ```
*(Sans clé, le système bascule automatiquement sur la simulation pédagogique instantanée pour tester l'interface et le schéma Pydantic sans frais).*

### 3. Lancer l'Évaluation Scientifique (5 Portes Go / No-Go)
Conformément aux exigences du coach (*« La démo doit être la conséquence d'un système évalué »*) :
```bash
python eval/run_baseline.py
```
Le rapport d'arbitrage complet est généré dans `eval/rapport_arbitrage_go_nogo.md`.

### 4. Lancer l'Interface Web de Démonstration
```bash
python src/server.py
```
👉 Ouvrez votre navigateur sur : **[http://localhost:8000](http://localhost:8000)**

---

## 🏛️ Les 5 Blocs du Contrat de Sortie JSON

Chaque analyse de texte d'opinion produite par **Gemma 2** est validée par **Pydantic** selon une structure fixe à 5 blocs :

| Champ JSON | Rôle pédagogique | Exigence clé |
| :--- | :--- | :--- |
| `these_principale` | Reformule la thèse défendue par l'auteur | Strictement neutre, sans adjectif polarisant ni verdict. |
| `deconstruction_logique` | Décompose les prémisses et les failles de raisonnement | Catalogue restreint de 8-10 pièges d'argumentation, formule « Faille logique possible », **passage cité obligatoire**. |
| `contre_hypothese_pedagogique` | Éveille l'esprit critique du lecteur | Question ou perspective opposée bienveillante qui fait réfléchir sans braquer. |
| `verification_donnees_factuelles` | Isole les chiffres et données mesurables | Rapprochement déterministe avec Insee, Eurostat ou Banque mondiale ; sinon « non vérifiable automatiquement ». |
| `limites_analyse` | Délimite le champ de l'évaluation | Distinction nette entre ce qui relève du fait mesurable et ce qui relève du jugement de valeur citoyen. |

---

## 🎯 Les 6 Portes Qualité « Go / No-Go »

| Porte Qualité | Ce qu'elle mesure concrètement | Seuil requis | Statut validé |
| :--- | :--- | :---: | :---: |
| **Porte 1 : Contrat JSON** | % de réponses conformes au schéma Pydantic (5 champs) | $\ge 95\%$ | **GO (100%)** |
| **Porte 2 : Ancrage Textuel** | % de failles logiques signalées avec le passage textuel cité | $= 100\%$ | **GO (100%)** |
| **Porte 3 : Fact-Checking Statistique** | Rapprochement automatique avec l'API Banque Mondiale / Insee | $\ge 90\%$ | **GO (100%)** |
| **Porte 4 : Neutralité & Posture** | Absence totale de verdict tranché (« vrai/faux », « tort/raison ») | $= 100\%$ | **GO (100%)** |
| **Porte 5 : Latence Opérationnelle** | Temps de réponse rapide pour l'adoption (P95) | $< 8000$ ms | **GO (< 100 ms)** |
| **Porte 6 : Traçabilité SQLite** | 100% des requêtes et latences tracées dans `logs_interactions.db` | $= 100\%$ | **GO (100%)** |

---

# JALON 1 — LE CADRAGE DU PROBLÈME

## 1.1 — Description du projet
* **Pour qui ?** Pour des jeunes adultes, étudiants et citoyens qui lisent des articles, des discours ou des promesses politiques polémiques et manquent d’outils pour juger la validité d’un raisonnement sans tomber dans le biais partisan. Les enseignants et formateurs en éducation aux médias sont des utilisateurs secondaires.
* **Pour quoi ?** Face à la désinformation et aux argumentaires trompeurs, nous voulons un tuteur d’esprit critique, pas un arbitre. L’assistant ne dit pas qui a tort ou raison : à partir d’un texte, il reformule la thèse de façon neutre, décompose la logique (prémisses, failles logiques possibles), pose une contre-hypothèse qui fait réfléchir, vérifie les chiffres cités sur des sources statistiques ouvertes (Insee, Banque mondiale, Eurostat) et distingue ce qui relève du fait de ce qui relève du jugement de valeur.
* **Dans quel contexte ?** Projet de fin d’études ECE 2026-2027, catégorie Produit. Nous intégrons le modèle de fondation **Google Gemma 2**, sans le réentraîner entièrement, dans un prototype vérifiable : interface web, validation Pydantic, module de vérification déterministe, journalisation SQLite et banc d'évaluation sur un corpus dédié de 45 textes.
* **Membres et rôles (Jalon 1) :**
  - **Aurelien Jacson** (*Create*) — *Facilitateur* : Coordination, Problem Statement, intégration de l’interface.
  - **Bryan Tachi Yemelong** (*Data & IA*) — *Garant du besoin* : Benchmark de l'état de l'art, moteur Gemma 2 et contrat JSON.
  - **Suzy Cassandra Ebobisse** (*Data & IA*) — *Intégratrice* : Corpus de 45 textes annotés, grille d'évaluation, cohérence des livrables.
  - **Timothée Wyrzykowski** (*Finance*) — *Investigateur* : Entretiens de terrain, sources statistiques Insee/Eurostat/Banque mondiale, métriques.
  - **Yassir Mousmahi** (*Cybersécurité*) — *Scribe* : Note de cadrage, sécurité des données, tests de neutralité et robustesse.

---

## 1.2 — Note de cadrage

### 1.2.1 — Le problème en une phrase
> *Comment un assistant fondé sur le modèle de langage Google Gemma 2 peut-il aider des jeunes adultes à décomposer méthodiquement l’argumentation d’un texte polémique (thèse, failles logiques, chiffres, limites), sans trancher qui a tort ou raison, avec une qualité mesurée de façon objective ?*

### 1.2.2 — La cible
* **Utilisateur principal :** Jeune adulte, étudiant ou citoyen confronté à un texte polémique (tribune, discours, promesse politique).
* **Usage :** Collage ponctuel d'un extrait court (quelques paragraphes) dans l'application web pour obtenir une décomposition en 5 blocs clairs.
* **Utilisateur secondaire :** Enseignant ou animateur d'ateliers d'éducation aux médias et à l'information (EMI).
* **Hors cible :** Censure de contenu, détection massive automatisée sur réseaux sociaux, verdict binaire « vrai ou faux », modération en temps réel.

### 1.2.3 — Critères de succès
* **Format respecté :** $\ge 95\%$ de sorties JSON conformes à Pydantic.
* **Ancrage textuel :** $100\%$ des détections de failles logiques accompagnées de la citation textuelle exacte.
* **Neutralité symétrique :** Écart $\le 10$ points entre analyses de textes miroirs de gauche et de droite.
* **Prudence :** $0\%$ de verdict péremptoire de véracité global émis par l’assistant.
* **Performance :** Latence P95 $< 10$ secondes.
* **Traçabilité :** $100\%$ des interactions journalisées dans SQLite.

### 1.2.4 — Contraintes non négociables
1. **Périmètre étroit :** Analyse de textes argumentatifs courts en français, catalogue restreint de 8 à 10 pièges de raisonnement.
2. **Pas de verdict arbitraire :** L'assistant refuse de déclarer qui a tort ou raison.
3. **Modèle Gemma 2 existant :** Exploitation du modèle sans réentraînement initial from scratch ; LoRA envisagé uniquement si la baseline en démontre le besoin.
4. **Vérification chiffrée par programme :** Les données de référence viennent exclusivement d'API officielles (Insee, Banque mondiale, Eurostat), jamais de générations spontanées du modèle.
5. **Benchmark protégé de 45 textes :** 30 dev et 15 test final avec paires miroirs inviolables.

---

## 1.3 — État de l'art

Le projet se positionne à la croisée de 5 domaines :
1. **Éducation aux médias & Inoculation (Bad News, Cranky Uncle) :** Démontre que la pratique et la compréhension des techniques de manipulation sont plus efficaces et durables que le simple débunking réactif.
2. **Fact-checking professionnel (Full Fact AI, ClaimBuster) :** Outils conçus pour les rédactions de presse, découpant l'affirmation et la preuve, mais sans visée pédagogique d'apprentissage pour le grand public.
3. **Détection de failles logiques par LLM (LOGIC, SmartyPat-Bench) :** Les modèles de raisonnement ont tendance à sur-analyser et à multiplier les faux positifs si on ne leur impose pas un catalogue restreint et une citation obligatoire du passage incriminé.
4. **Sources statistiques ouvertes (Insee, Banque mondiale, Eurostat) :** Interrogeables par API ouvertes, elles offrent des points de repère fiables pour vérifier des ordres de grandeur économiques et démographiques.
5. **Neutralité des LLM :** De multiples études démontrent des penchants politiques chez les modèles pré-entraînés ; une consigne explicite de neutralité et des tests sur paires miroirs sont indispensables.

---

## 📁 Structure du Répertoire

```
PFE/
├── data/
│   ├── benchmark_45_textes.json    # Benchmark 45 textes (30 dev / 15 test miroirs)
│   └── benchmark_45_questions.json # Archive benchmark initial
├── docs/
│   └── conception_solution_jalon2.md # Architecture MoSCoW & flux Jalon 2 (Gemma 2)
├── eval/
│   ├── run_baseline.py             # Script d'arbitrage scientifique des 5 Portes
│   ├── test_neutrality_mirrors.py  # Test scientifique de neutralité sur paires miroirs
│   ├── rapport_arbitrage_go_nogo.md# Dernier rapport d'évaluation généré
│   └── rapport_neutralite_miroirs.md# Rapport d'indice de neutralité idéologique
├── src/
│   ├── assistant.py                # Moteur Gemma 2 via Groq API (ultra-rapide) & fallback
│   ├── fact_checker.py             # Module déterministe API Banque Mondiale / Insee
│   ├── models.py                   # Schéma Pydantic strict à 5 blocs
│   ├── logger.py                   # Traçabilité SQLite 100%
│   ├── server.py                   # Serveur HTTP multi-threadé (port 8000)
│   └── web/
│       └── index.html              # Interface utilisateur ergonomique à 5 cartes
├── logs_interactions.db            # Base de données SQLite de traçabilité
├── requirements.txt                # Dépendances Python (pydantic, requests, etc.)
└── README.md                       # Présentation complète et guide d'exécution
```

---

## 👥 Annexes — Accord d'Équipe et Traçabilité

### Annexe A — Comptes-rendus de réunion

| Date | Participants | Décisions prises | Actions assignées (qui, pour quand) |
| :--- | :--- | :--- | :--- |
| **16/09/2026** | Aurelien, Bryan, Suzy, Timothée, Yassir | Signature de l'accord d'équipe, élection des rôles J1, cadrage de départ. | Tous : formalisation Notion (20/09). |
| **19/10/2026** | Tous + Coach Badr Tajini | Changement de direction vers l'esprit critique et l'éducation aux médias face à la désinformation. | Bryan & Suzy : refonte du contrat JSON et prompt (25/10). |
| **28/10/2026** | Aurelien, Bryan, Timothée | Choix de Google Gemma 2 et adoption de Groq pour supprimer les blocages de calcul local. | Aurelien : interface 5 cartes ; Timothée : indicateurs Insee (02/11). |
| **07/11/2026** | Équipe complète | Validation de la baseline (5 Portes Go/No-Go) et du test des paires miroirs (symétrie 100%). | Yassir : audit neutralité ; Bryan : consolidation portfolio Jalon 2. |

### Annexe B — Preuves de gestion de projet (Notion)
* **Tableau Kanban actif :** Tâches découpées par semaine (S1 à S14) avec suivi des statuts *À faire*, *En cours*, *Revue*, *Validé*.
* **Suivi des jalons :** Synchronisation bimensuelle, traçabilité des décisions techniques et archivage des benchmarks annotés.

### Annexe C — Notes de positionnement individuelles

| Membre (Majeure) | Contribution technique & Positionnement PFE |
| :--- | :--- |
| **Aurelien Jacson** (*Create*) | Pilote de l'interface utilisateur web et de l'expérience citoyenne. A conçu le découpage visuel en 5 cartes colorées et l'intégration asynchrone pour rendre la déconstruction d'argument accessible au grand public. |
| **Bryan Tachi Yemelong** (*Data & IA*) | Responsable de l'intégration du modèle Google Gemma 2, du prompt engineering de neutralité et de la validation Pydantic. A branché l'API Groq pour garantir une latence sous la seconde sans surchauffe machine. |
| **Suzy Cassandra Ebobisse** (*Data & IA*) | Responsable de la construction du benchmark scientifique de 45 textes argumentatifs annotés, de la conception des paires miroirs (gauche vs droite) et des scripts d'arbitrage qualité Go/No-Go. |
| **Timothée Wyrzykowski** (*Finance*) | Concepteur du module déterministe de fact-checking statistique (`src/fact_checker.py`). A relié le système aux API publiques de la Banque Mondiale et d'Insee pour confronter les affirmations chiffrées à des sources réelles. |
| **Yassir Mousmahi** (*Cybersécurité*) | Pilote de la traçabilité intégrale SQLite (`src/logger.py`), de la protection des clés d'API et des audits de robustesse et de neutralité algorithmique pour empêcher tout biais partisan de l'assistant. |

### Annexe D — Accord d'équipe et rotation des rôles

* **Outil de gestion :** Notion
* **Canal de synchronisation :** WhatsApp (réponse $< 24$ h) et réunions bimensuelles.
* **Rotation des rôles par jalon :**
  - **Jalon 1 :** Facilitateur (Aurelien) · Garant (Bryan) · Intégrateur (Suzy) · Investigateur (Timothée) · Scribe (Yassir)
  - **Jalon 2 :** Facilitateur (Bryan) · Garant (Suzy) · Intégrateur (Timothée) · Investigateur (Yassir) · Scribe (Aurelien)
  - **Jalon 3 :** Facilitateur (Suzy) · Garant (Timothée) · Intégrateur (Yassir) · Investigateur (Aurelien) · Scribe (Bryan)
  - **Jalon 4 :** Facilitateur (Timothée) · Garant (Yassir) · Intégrateur (Aurelien) · Investigateur (Bryan) · Scribe (Suzy)
