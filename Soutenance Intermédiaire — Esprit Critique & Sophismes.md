ECE ING5 · PFE 2026-2027

Assistant Pédagogique — Esprit Critique & Sophismes

Soutenance Intermédiaire · J2

[Contexte](#contexte) [Besoin](#besoin) [Problématique](#problematique) [État de l'art](#etatdelart) [Positionnement](#opportunite) [Solution](#solution) [Risques](#risques) [Sources](#refs)

01 — Contexte

## Un environnement informationnel dégradé, des citoyens peu outillés

6× plus vite que la vérité — vitesse de propagation des fausses informations sur les réseaux Vosoughi, Roy & Aral, Science, 2018 \[1\]

36 % des Européens exposés à de la désinformation au moins plusieurs fois par semaine Eurobaromètre FL014EP, 2025 \[2\]

29 % de confiance dans les médias en France — l'un des taux les plus bas d'Europe Reuters Institute Digital News Report, 2022 \[3\]

La désinformation ne se propage pas malgré les algorithmes, mais grâce à eux : une étude portant sur 126 000 contenus partagés par 3 millions d'utilisateurs montre que les fausses nouvelles touchent plus de personnes, plus rapidement, et en mobilisant davantage les émotions que les informations vraies **\[1\]**. Ce phénomène s'aggrave à mesure que des outils d'IA générative abaissent le coût de production de contenu trompeur.

Au niveau réglementaire, le **Digital Services Act (DSA, 2022)** impose aux grandes plateformes d'évaluer et de réduire les risques systémiques liés à la désinformation **\[4\]**. L'**European Digital Media Observatory (EDMO)** coordonne les fact-checkers européens, mais reconnaît dans ses enquêtes que seul un citoyen sur cinq connaît l'existence du DSA **\[5\]**.

Le problème n'est donc pas uniquement la disponibilité de l'information vraie : c'est **l'absence d'outils permettant aux citoyens d'analyser la mécanique argumentative d'un discours**, indépendamment de sa vérité factuelle. Un argument peut être rhétoriquement solide et factuellement faux ; il peut aussi être sincère et logiquement défaillant.

**Acteurs principaux :** organisations de fact-checking (AFP Factuel, Les Décodeurs, FactCheck.org), institutions éducatives (CLEMI en France), plateformes soumises au DSA, chercheurs en argumentation computationnelle (ACL, EMNLP, NAACL).

---

02 — Besoin

## Savoir si c'est faux ne suffit pas : il faut comprendre pourquoi c'est trompeur

Les outils de fact-checking existants répondent à la question *« cette affirmation est-elle vraie ou fausse ? »*. Ils ne répondent pas à la question *« quelle technique argumentative est utilisée, et pourquoi peut-elle induire en erreur ? »*.

Or, la recherche en psychologie sociale montre que la simple correction d'une fausse information (*debunking*) a un effet limité, voire contre-productif, sur les croyances préexistantes — c'est l'**effet de persévérance des croyances**. À l'inverse, **enseigner les mécanismes de manipulation avant l'exposition** (*prebunking*, ou « inoculation ») réduit significativement l'efficacité de ces mécanismes \[6\]\[7\].

Notre public cible est le **jeune adulte étudiant** (1re–3e cycle), utilisateur quotidien de réseaux sociaux et d'assistants IA, qui consomme de l'argumentation sans avoir appris à en décoder la structure formelle. Les enseignements de logique et de rhétorique sont absents de la grande majorité des cursus français du supérieur.

**Hypothèses à valider (entretiens prévus) :**

H1

Les étudiants identifient intuitivement qu'un argument « ne semble pas juste » sans pouvoir nommer le mécanisme en cause.

H2

Nommer un sophisme (« c'est une corrélation confondue avec la causalité ») est plus mémorable qu'une simple réfutation.

H3

Une réponse structurée en 4 blocs (thèse, déconstruction, exemple, vérification) est perçue comme plus utile qu'une réponse libre.

H4

Les étudiants font confiance aux réponses d'un assistant IA sans chercher à vérifier leur exactitude sur ce type de contenu.

---

03 — Problématique

## La question à laquelle le projet répondra

Dans quelle mesure un assistant LLM à réponse structurée aide-t-il des étudiants à nommer correctement les sophismes formels, comparé à une réponse libre, sur un corpus de cas canoniques ?

**Pourquoi cette formulation est testable :** le corpus de cas canoniques (exemples dont le sophisme de référence est établi et non ambigu) permet de comparer mécaniquement la réponse obtenue à la réponse attendue. La comparaison *baseline* (prompt libre) vs *structured* (sortie JSON contrainte) mesure l'apport du format. La relecture humaine sur un échantillon juge l'exactitude et la valeur pédagogique.

**Ce qu'elle n'est pas :** la problématique ne demande pas si l'assistant « sait » si une affirmation est vraie ou fausse. Elle demande s'il peut décoder la *mécanique argumentative* d'un texte. Ces deux questions sont distinctes et la seconde est celle que les outils existants ne traitent pas.

**Périmètre :** sophismes formels classiques, liste fermée (\~15 types), exemples fabriqués ou canoniques documentés. Hors périmètre : analyse de vrais discours politiques non annotés, vérification factuelle.

Ad hominem Pente glissante Homme de paille Faux dilemme Appel à l'autorité Corrélation ≠ causalité Ad populum Généralisation hâtive Whataboutism Cherry picking Fausse analogie Appel aux émotions Pétition de principe Ad ignorantiam Nirvana fallacy

---

04 — État de l'art

## Ce qui existe — et ce qui manque

L'analyse de l'existant révèle quatre familles de solutions distinctes, toutes partielles au regard de notre besoin.

### A. Outils de fact-checking automatique

ClaimBuster

Modèle NLP (KDD 2017) qui classe les phrases selon leur « mérite à être vérifiées ». Entraîné sur des débats électoraux américains.

Juge l'importance de vérifier, pas la structure de l'argument. Ne détecte pas les sophismes. \[8\]

Full Fact AI

Utilisé par +40 organisations dans 30 pays. Classe les affirmations par priorité et cherche des correspondances dans une base de vérifications existantes.

Opère sur des claims factuels. Aucun composant d'analyse rhétorique ou de détection de sophisme. \[9\]

NewsGuard

Score 0-100 basé sur 9 critères éditoriaux (transparence, rigueur…) appliqués à des sources, pas à des arguments individuels.

Évalue la fiabilité d'une source, pas la validité d'un raisonnement. \[10\]

### B. Outils de cartographie argumentative

Kialo / Kialo Edu

Arbre pro/con construit manuellement par les utilisateurs. Version éducative utilisée en classe pour structurer des débats.

100 % manuel. Aucune analyse automatique. Utile en classe mais non scalable. \[11\]

Argdown

Langage de balisage textuel pour cartes argumentatives (support, attaque, undercut). Exporte SVG, JSON, HTML.

Outil de représentation, pas d'analyse. Requiert une expertise en logique formelle. \[12\]

IBM Project Debater

Système IA capable de débattre oralement sur des sujets complexes. Entraîné sur 400M d'articles. Prix Nature 2021.

Génère des arguments, ne détecte pas les sophismes. Usage expérimental, non pédagogique. \[13\]

### C. Recherche en détection automatique de sophismes

La détection automatique des sophismes est un domaine de recherche actif mais difficile. Les résultats récents montrent que les LLMs peinent sans structure imposée :

| Travail | Contribution | Résultat clé |
| --- | --- | --- |
| Jin et al., EMNLP 2022 \[14\] | Dataset Logic + LogicClimate. Benchmark de détection de sophismes. | Un classifieur structuré bat le meilleur LLM de +5,46 F1. Les LLMs sans structure échouent. |
| Helwe et al. (MAFALDA), NAACL 2024 \[15\] | Fusion de datasets, taxonomie unifiée, annotations expertes avec explications. | Benchmark de référence pour l'évaluation. Montre que la subjectivité est le principal obstacle à la mesure. |
| Li et al., arXiv 2025 \[16\] | Survey LLMs en argumentation mining. | LLMs sur-prédisent les arguments dans les textes émotionnels. Fiabilité LLM-as-judge discutée. |
| Habernal et al., EMNLP 2017 \[17\] | Serious game Argotario pour collecter des exemples de sophismes. | 5 types de sophismes collectés. Montre la viabilité d'une approche par exemples canoniques. |

**Leçon directe pour notre projet :** les cas non ambigus (sophismes canoniques avec un seul label correct) sont mesurables. Les cas nuancés ne le sont pas. Notre corpus doit rester dans la première catégorie.

### D. Approches pédagogiques : prebunking et lecture latérale

La recherche en psychologie sociale converge vers une conclusion contre-intuitive : **enseigner les mécanismes de manipulation est plus efficace que corriger les erreurs après coup.**

Théorie de l'inoculation (prebunking)

7 expériences, \~30 000 participants. Des micro-vidéos expliquant les techniques de désinformation ont été vues par 5M de personnes sur YouTube, avec un effet positif mesurable sur la résistance à la manipulation.

Roozenbeek, van der Linden et al., Science Advances, 2022 \[6\]

SIFT Method (Caulfield, 2019)

Stop, Investigate the source, Find better coverage, Trace claims. Méthode pratique pour évaluer une information, largement adoptée dans l'éducation aux médias américaine.

Répond à « est-ce fiable ? », pas à « quelle est la mécanique argumentative ? » \[18\]

Lateral Reading (Stanford, 2017)

Les fact-checkers experts quittent le site pour vérifier ailleurs. Contrairement aux historiens et étudiants, ils ne s'arrêtent pas à l'apparence de la source.

Wineburg & McGrew \[19\]. Compétence enseignable, mais distincte de l'analyse de sophismes.

---

05 — Opportunité & positionnement

## L'angle que personne n'occupe

Matrice de positionnement

| Outil | Vérifie les faits | Analyse la structure | Nomme le sophisme | Pédagogique | Évaluable |
| --- | --- | --- | --- | --- | --- |
| ClaimBuster / Full Fact | ✓ | ✗ | ✗ | ✗ | partiel |
| Kialo / Argdown | ✗ | ✓ (manuel) | ✗ | partiel | ✗ |
| SIFT / Lateral Reading | partiel | ✗ | ✗ | ✓ | partiel |
| ChatGPT / Claude (libre) | partiel | partiel | partiel | partiel | ✗ |
| **Notre assistant (structuré)** | hors périmètre | ✓ | ✓ | ✓ | ✓ |

Notre approche s'inscrit dans la logique du **prebunking** (inoculation) : plutôt que de dire « cette affirmation est fausse », l'assistant enseigne *quel mécanisme rhétorique est à l'œuvre et pourquoi il peut induire en erreur*. Cette posture est cohérente avec les résultats de van der Linden et al. \[6\] et avec l'absence d'outil pédagogique structuré dans cet espace.

Le verrou que nous levons est **l'évaluabilité** : en limitant le périmètre aux sophismes canoniques (liste fermée, exemples fabriqués), nous obtenons une ground truth non ambiguë qui rend la comparaison baseline/structured reproductible et la notation humaine fiable.

---

06 — Solution envisagée

## Ce que nous allons construire en Phase 3

Notre Prototype Fonctionnel est un **assistant pédagogique de détection de sophismes** : l'utilisateur soumet un argument en texte libre, l'assistant identifie le type de sophisme, déconstruit son mécanisme, et fournit un exemple contre-factuel. La réponse est structurée en 4 blocs fixes, ce qui permet une évaluation objective et reproductible.

En deux phrases : l'utilisateur colle un argument. L'assistant répond avec (1) le nom du sophisme, (2) pourquoi il est trompeur, (3) un exemple similaire, (4) comment le détecter soi-même — en s'appuyant sur une liste fermée de 15 types.

**La fonctionnalité la plus risquée** — et donc celle sur laquelle se concentre le prototype — est la *cohérence de la classification* : un LLM avec prompt structuré nomme-t-il le bon sophisme de façon reproductible sur un corpus annoté, mieux qu'un prompt libre ? C'est la question que notre pipeline d'évaluation (runner baseline/structured + CSV de résultats) est conçu pour trancher avant la soutenance finale.

**Ce que nous ne ferons pas dans cette version :** vérification factuelle des affirmations, analyse de vrais discours non annotés, fine-tuning de modèle. Ces choix libèrent du temps pour soigner ce qui compte : la qualité du corpus et la rigueur du protocole d'évaluation.

### Priorisation MoSCoW

| Priorité | Fonctionnalité | Justification |
| --- | --- | --- |
| Must | Prompt structuré forçant la classification parmi une liste fermée de 15 sophismes | C'est l'hypothèse centrale à tester. Sans liste fermée, l'évaluation automatique est impossible. |
| Must | Format de sortie 4 blocs : Reformulation → Mécanisme → Exemple → Vérification | Chaque bloc est scorable indépendamment. Condition nécessaire à la comparaison baseline/structured. |
| Must | Corpus d'évaluation (≥ 30 cas canoniques annotés avec label de référence) | Sans ground truth, rien n'est mesurable. La qualité du corpus détermine la validité des résultats. |
| Must | Pipeline de comparaison baseline vs structured avec export CSV | Requis par le guide de projet. Permet une évaluation reproductible et partageable avec le coach. |
| Should | Interface Gradio (entrée texte libre + affichage des 4 blocs) | Nécessaire pour les tests utilisateurs en Phase 3. Peut fonctionner en local dans un premier temps. |
| Should | ≥ 3 cas par type de sophisme dans le corpus (couverture équilibrée) | Évite que les résultats soient dominés par 2–3 types surreprésentés. Faisable avec `generate_questions.py`. |
| Could | Mode entraînement : l'utilisateur devine le sophisme avant de voir la réponse | Renforce le prebunking actif (apprentissage par prédiction). Dépend du temps disponible après les Must. |
| Could | Déploiement public sur Hugging Face Spaces | Utile pour le recrutement de testeurs. Non critique pour valider l'hypothèse principale. |
| Won't | Vérification factuelle des affirmations | Hors périmètre : nous analysons la mécanique argumentative, pas la vérité des faits. Confondre les deux affaiblit le concept. |
| Won't | Analyse de vrais discours politiques non annotés | Les cas ambigus rendent l'évaluation subjective. La validité du prototype repose sur des cas canoniques. |
| Won't | Fine-tuning d'un modèle de langage | Infrastructure GPU et volume de données insuffisants en contexte étudiant. L'ingénierie de prompt suffit pour tester l'hypothèse. |

### Arbre de choix n°1 — Fournisseur LLM

Quatre options évaluées sur trois critères objectifs : **coût** (budget étudiant = 0 €), **déployabilité cloud sans GPU**, et **taille du modèle** (≥ 30B pour des performances suffisantes sur la classification).

Coût = 0 € ?

Non

**OpenAI GPT-4o** \~0,03 $/1 k tokens · hors budget étudiant · écarté d'emblée

Oui → cloud sans GPU ?

Non

**Ollama (local)** Gratuit, GPU requis pour 70B · pas de déploiement HF Spaces · écarté pour le proto cloud

Oui → modèle ≥ 30B ?

Non

**Together AI / Gemma 7B** Gratuit, cloud, mais 7B trop petit pour la classification fine · écarté en principal

Oui

**Groq — Llama-3.3-70B ✓ Retenu** Gratuit · API OpenAI-compatible · 70B · latence \< 2 s · Together AI disponible en fallback

**Hypothèse résiduelle à valider en Phase 3 :** Llama-3.3-70B sans fine-tuning atteint une précision ≥ 65 % sur la liste fermée avec prompt structuré. Pivot si non : réduire à 8 sophismes les plus distincts, ou basculer sur GPT-4o-mini (\< 5 € pour 1 000 évaluations).

### Arbre de choix n°2 — Stratégie de prompt

Trois approches comparées sur le critère clé : *la sortie est-elle évaluable automatiquement ?*

| Stratégie | Description | Éval. auto. | Verdict |
| --- | --- | --- | --- |
| Baseline (libre) | Prompt minimal : « Analyse cet argument. » | Non | Conservé comme référence de comparaison. |
| **Structured (JSON contraint)** | Sortie JSON avec clés `fallacy_name`, `mechanism`, `example`, `verification` | Oui | **Retenu.** La clé `fallacy_name` est comparable directement au label de référence. |
| Few-shot | 2–3 exemples résolus dans le prompt avant la question | Oui | Testé en variante optionnelle. Coût en tokens +40 %. Intégré si structured insuffisant. |

---

07 — Risques identifiés

## Ce qui pourrait faire dérailler la Phase 3 — et nos plans de secours

| Risque | Probabilité | Impact | Plan de mitigation |
| --- | --- | --- | --- |
| **Ambiguïté des labels** — Un même argument peut relever de plusieurs sophismes selon l'interprétation (ex : ad hominem vs whataboutism). | Forte | Fort | Restreindre le corpus à des cas canoniques fabriqués, non ambigus. Rédiger un guide d'annotation avant toute notation. Mesurer l'accord inter-annotateurs (κ) sur 10 % du corpus. |
| **Performances LLM insuffisantes** — Le modèle nomme systématiquement le mauvais sophisme même avec un prompt structuré. | Moyenne | Fort | Évaluer sur le dev set en semaine 1 de Phase 3. Pivot 1 : réduire à 8 types les plus distincts. Pivot 2 : passer à GPT-4o-mini (\< 5 € pour 1 000 évals). Le runner est agnostique au modèle (`--model` flag). |
| **Dépendance API Groq** — L'API gratuite devient payante, subit un rate limit bloquant, ou est indisponible en période de pic. | Faible | Fort | L'adaptateur `ChatCompletionsClient` est agnostique au fournisseur. Basculer sur Together AI ou Ollama local sans modifier le code (`--provider` flag). |
| **Corpus trop petit** — Avec 30 cas dev, un écart de 5 % représente 1–2 cas : statistiquement non significatif. | Moyenne | Moyen | Utiliser `generate_questions.py` pour atteindre 50+ cas (≥ 3 exemples / type). Chaque membre valide un batch de 10 questions en parallèle. |
| **Désaccord inter-annotateurs** — Les membres de l'équipe ne scorent pas de la même façon la qualité pédagogique d'une réponse. | Forte | Moyen | Rédiger un guide de scoring humain avec exemples calibrés (0 / 1 / 2 par bloc) avant tout scoring. Cross-noter 10 % du corpus à 2 personnes et calculer l'accord avant de valider. |
| **Recrutement des testeurs utilisateurs** — Les étudiants disponibles pour les tests UX sont difficiles à mobiliser en cours d'année. | Forte | Moyen | Contacter 10 volontaires dès J1 de Phase 3. Protocole alternatif : test en binôme de 15 min pendant une pause de cours (3 arguments fournis, réponses notées sur papier). |

**Risques liés :** les risques 1 (ambiguïté) et 5 (désaccord humain) se résolvent par le même investissement en amont — un guide d'annotation rigoureux rédigé *avant* de scorer la moindre réponse. C'est la première action planifiée en Phase 3.

---

08 — Références

## Sources

- Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. *Science*, 359(6380), 1146–1151. DOI 10.1126/science.aap9559
- Parlement européen. (2025). Flash Eurobarometer FL014EP — Social Media Survey. data.europa.eu
- Reuters Institute. (2022). Digital News Report 2022 — France. reutersinstitute.politics.ox.ac.uk
- Règlement (UE) 2022/2065 du Parlement européen et du Conseil (Digital Services Act), Art. 34–35. EUR-Lex CELEX 32022R2065
- EDMO / CEDMO. (2024). Opinion tracking survey — 9 EU countries. edmo.eu
- Roozenbeek, J., van der Linden, S., Goldberg, B., Rathje, S., & Lewandowsky, S. (2022). Psychological inoculation improves resilience against misinformation on social media. *Science Advances*, 8(34). DOI 10.1126/sciadv.abo6254
- Lewandowsky, S., & van der Linden, S. (2021). Countering Misinformation and Fake News Through Inoculation and Prebunking. *European Review of Social Psychology*, 32(2), 348–384. DOI 10.1080/10463283.2021.1876983
- Hassan, N., Arslan, F., Li, C., & Tremayne, M. (2017). Toward Automated Fact-Checking: Detecting Check-worthy Factual Claims by ClaimBuster. *KDD 2017*, pp. 1803–1812.
- Full Fact. (2024). Full Fact AI — Automated claim monitoring. fullfact.org/ai/
- NewsGuard. (2024). Rating Process and Criteria. newsguardtech.com/ratings/rating-process-criteria/
- Kialo. (2024). Kialo Edu — Collaborative argumentation platform. kialo-edu.com
- Betz, G., et al. (2021). Argdown — A syntax for argument mapping. argdown.org
- Slonim, N., et al. (2021). An autonomous debating system. *Nature*, 591, 379–384. DOI 10.1038/s41586-021-03215-w
- Jin, Z., et al. (2022). Logical Fallacy Detection. *Findings of EMNLP 2022*, pp. 7180–7198. DOI 10.18653/v1/2022.findings-emnlp.532
- Helwe, C., Calamai, S., Paris, P.-L., Clavel, C., & Suchanek, F. (2024). MAFALDA: A Benchmark and Comprehensive Study of Fallacy Detection and Classification. *NAACL 2024*, pp. 4810–4845. arXiv:2311.09761
- Li, R., et al. (2025). Large Language Models in Argument Mining: A Survey. arXiv:2506.16383
- Habernal, I., et al. (2017). Argotario: Computational Argumentation Meets Serious Games. *EMNLP System Demonstrations*, pp. 7–12. ACL Anthology D17-2002
- Caulfield, M. (2019). SIFT (The Four Moves). hapgood.us
- Wineburg, S., & McGrew, S. (2017). Lateral Reading: Reading Less and Learning More When Evaluating Digital Information. Stanford History Education Group Working Paper.