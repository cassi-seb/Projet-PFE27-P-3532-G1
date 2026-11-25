# 🎯 Plan de Remédiation Stratégique — Soutenance PFE
## Réponses Complètes aux Retours des Jurys (Axel VINANT & Taha RIDENE)
**Projet :** Assistant Pédagogique d'Esprit Critique & Déconstruction d'Arguments  
**Équipe :** PFE27-P-3532  

---

## 1. Synthèse et Diagnostic des Retours

| Membre du Jury | Nature des critiques | Ce qu'il faut corriger impérativement |
| :--- | :--- | :--- |
| **Axel VINANT** | **Forme, Clarté & Posture Ingénieur** | - Éliminer les slides surchargées et le jargon non maîtrisé (ex: "dessiner un débat à la main").<br>- Créer un **fil conducteur évident** centré sur un cas d'usage utilisateur concret.<br>- Dépasser l'argument étudiant « c'est gratuit » : présenter une **vraie vision d'architecture industrielle et scalable**. |
| **Taha RIDENE** | **Rigueur Scientifique, Data & Sécurité** | - Détailler le fonctionnement exact et les fonctionnalités.<br>- Donner des **ordres de grandeur chiffrés** (utilisateurs, volumes, coûts, ressources).<br>- Formaliser la **stratégie de données** (collecte, annotation, qualité).<br>- Exposer les **garde-fous de sécurité** (sécurisation des sorties, anti-hallucination).<br>- Présenter la **méthodologie d'évaluation** (critères objectifs, portes qualité). |

---

## 2. Réponses Détaillées aux Retours d'Axel VINANT

### 2.1. Le Fil Conducteur Utilisateur (User Story concrète)
**Problème soulevé :** *« On ne comprend pas comment votre solution va servir à l'utilisateur. Ça manque d'exemples. »*  
**Notre réponse à présenter en soutenance :**  
> *"Prenons le cas de Lucas, 20 ans, étudiant. En naviguant sur les réseaux sociaux, il tombe sur une tribune virale affirmant : 'Le chômage a bondi à 25% ! Soit nous coupons immédiatement toutes les aides sociales, soit notre économie fera faillite d'ici six mois.' Face à ce texte anxiogène, que fait Lucas ?*  
> *Aujourd'hui, il a deux choix insatisfaisants : croire aveuglément ou chercher sur Google pendant 45 minutes sans savoir à qui faire confiance. Avec notre solution, Lucas colle l'extrait. En 2 secondes, notre assistant lui fournit 4 clés de discernement :*  
> *1. La détection du piège de raisonnement : un Faux Dilemme ('tout noir ou tout blanc') et un scénario catastrophe non prouvé.*  
> *2. La vérification chiffrée : l'API de la Banque Mondiale montre que le chômage réel en France est à 7.54%, pas 25%.*  
> *3. Une question pour ouvrir la réflexion sans lui imposer une opinion.*  
> *4. La distinction entre le fait vérifiable (le chiffre) et le débat citoyen (la politique sociale).*  
> *Notre assistant n'est pas un tribunal d'opinion : c'est une boussole d'esprit critique."*

### 2.2. Élimination du Jargon Inutile
* **Suppression totale** des références théoriques confuses sur les cartographies manuelles de débats (*"dessiner un débat à la main"*).
* Chaque slide doit respecter la règle : **1 idée clé = 1 titre percutant + 1 visuel ou métrique + 3 lignes de texte maximum.**

### 2.3. Choix Techniques : La Vision Industrielle (Scale-up au-delà du "Gratuit")
**Problème soulevé :** *« Choix techniques faits avec une vision étudiante 'il faut que ça soit gratuit'. Si vous vouliez vraiment développer cette solution, vous feriez quels choix techniques ? »*  
**Notre feuille de route d'industrialisation (Production-Ready) :**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       ARCHITECTURE INDUSTRIELLE CIBLE (SCALE-UP)                │
└─────────────────────────────────────────────────────────────────────────────────┘
  Navigateurs / Apps Clients (100k+ requêtes/jour)
            │
            ▼ HTTPS / Cloudflare WAF (Protection DDoS & Rate Limiting)
  ┌─────────────────────────────────────────────────────────────┐
  │ API Gateway (FastAPI / Traefik / Kubernetes EKS)            │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
         ┌───────────────────────┼──────────────────────────────┐
         ▼                       ▼                              ▼
  ┌──────────────┐      ┌─────────────────┐           ┌──────────────────┐
  │ Cache Sémant.│      │ Fact-Checking   │           │ Moteur Inférence │
  │ Redis        │      │ Déterministe    │           │ vLLM / TensorRT  │
  │ (Hit: <10ms) │      │ Data Pipeline   │           │ GPU A10G / L4    │
  │ Réduit coûts │      │ (Insee/Banque M)│           │ Autoscaling KEDA │
  └──────────────┘      └─────────────────┘           └──────────────────┘
                                 │                              │
                                 └──────────────┬───────────────┘
                                                ▼
                                 ┌──────────────────────────────┐
                                 │ Observabilité & Traçabilité  │
                                 │ Langfuse + Prometheus/Grafana│
                                 └──────────────────────────────┘
```

1. **Moteur d'inférence en propre (Self-hosted Inférence) :**
   - Remplacement des API tierces par un cluster **vLLM** ou **TensorRT-LLM** déployé sur des instances GPU managées (**AWS EC2 G5 avec GPU NVIDIA A10G** ou **GCP avec NVIDIA L4**).
   - **Quantification AWQ/FP8** de Gemma 2 pour doubler le débit (throughput > 150 tokens/s par GPU).
   - Autoscaling horizontal avec **KEDA** (Kubernetes Event-driven Autoscaling) selon la file d'attente de requêtes.
2. **Cache Sémantique (Redis Semantic Cache) :**
   - Les débats d'actualité provoquent des questions similaires (ex: même discours politique collé par 5 000 utilisateurs).
   - Mise en cache des embeddings : si la similarité cosinus $> 0.95$, la réponse est servie en **< 10 ms sans réinterroger le LLM**, réduisant les coûts GPU de 40 à 60%.
3. **Observabilité & Monitoring Industriel :**
   - Remplacement de SQLite local par **PostgreSQL managé (AWS RDS)** pour la traçabilité.
   - Suivi en temps réel des dérives de prompt et latences via **Langfuse** et métriques **Prometheus / Grafana**.
4. **Modèle Économique & Coûts d'échelle chiffrés :**
   - Coût estimé pour **50 000 requêtes/jour** :
     - 2 instances GPU AWS A10G spot/réservées : ~450 $/mois.
     - Cache Redis + Ingestion données : ~50 $/mois.
     - **Coût de revient par analyse : ~0,0003 €** (extrêmement rentable pour un modèle SaaS éducatif ou institutionnel subventionné).

---

## 3. Réponses Détaillées aux 5 Points de Taha RIDENE

### Point 1 : Objectifs, Fonctionnalités et Fonctionnement
* **Objectif central :** Fournir aux citoyens et étudiants un tuteur automatisé d'esprit critique capable de déconstruire un discours en 5 blocs standardisés sans biais partisan.
* **Architecture modulaire :**
  1. *Module de Déconstruction Argumentative :* Repérage des 15 pièges fréquents avec citation textuelle.
  2. *Module de Fact-Checking Déterministe :* Vérification automatique des grandeurs macroéconomiques via API Banque Mondiale et Insee.
  3. *Module de Posture Pédagogique :* Formulation d'une contre-hypothèse bienveillante et distinction fait vs opinion.

### Point 2 : Ordres de Grandeur du Projet
* **Cible initiale :** 15 000 étudiants et lycéens en Île-de-France (ateliers d'Éducation aux Médias et à l'Information - EMI).
* **Volumétrie en production cible :** 100 000 analyses/mois.
* **Dimensionnement technique du prototype :**
  - Corpus de test : 45 textes calibrés (30 dev, 15 test miroirs).
  - Catalogue de référence : 15 pièges d'argumentation formellement définis (`fallacy_catalog.jsonl`).
  - Périmètre factuel : 5 séries macroéconomiques fondamentales (chômage, inflation, dette, PIB, population).
  - Latence opérationnelle observée : **P95 < 150 ms** en simulation / **~1,2 s** via API cloud.

### Point 3 : Stratégie de Gestion des Données (Data Governance)
1. **Collecte & Sourçage :** Corpus issu d'extraits réels de débats parlementaires, tribunes médiatiques et publications virales.
2. **Annotation & Qualification :**
   - Double annotation humaine à l'aveugle pour étiqueter les pièges d'argumentation et les chiffres cités.
   - Calcul de l'accord inter-annotateurs (score Cohen's Kappa cible $\ge 0.75$).
3. **Partitionnement étanche :**
   - 30 textes *dev* (ouverts pour le raffinement des prompts et des règles).
   - 15 textes *test* protégés (inviolables, contenant des paires miroirs symétriques gauche/droite pour mesurer l'absence d'overfitting).
4. **Sources de Référence Primaires :** Utilisation exclusive de bases de données publiques certifiées (Banque Mondiale Open Data API, Insee BDM, Eurostat).

### Point 4 : Sécurité, Garde-fous (Guardrails) & Fiabilité
1. **Zéro Hallucination Chiffrée :** Le LLM n'a **pas le droit d'inventer des chiffres**. Tout chiffre statistique provient du module Python déterministe branché directement sur l'API Banque Mondiale.
2. **Contrat de Sortie Strict Pydantic :** Toute sortie LLM est interceptée et validée par le schéma Pydantic (`ArgumentAnalysisResponse`). Si un champ manque ou si le format dévie, l'analyse est assainie avant affichage.
3. **Posture Non-Arbitre (Safety Algorithmique) :**
   - Règle système interdisant formellement les verdicts péremptoires (*« C'est faux »*, *« Vous avez tort »*).
   - Protection contre le biais de confirmation : l'assistant n'exprime aucun parti pris politique.
4. **Défense Anti-Injection :** Assainissement des balises HTML et des caractères d'échappement pour empêcher les attaques par jailbreak ou prompt injection.

### Point 5 : Méthodologie d'Évaluation Rigoureuse (Les 6 Portes Go/No-Go)
Chaque version du système doit obligatoirement franchir **6 Portes Qualité automatisées** :

| Porte Qualité | Indicateur Mesuré | Formule / Critère | Seuil Exigé | Résultat Obtenu |
| :--- | :--- | :--- | :---: | :---: |
| **Porte 1 : Contrat JSON** | Conformité Pydantic | Nombre de sorties 100% validées / Total | $\ge 95\%$ | **100% (GO)** |
| **Porte 2 : Ancrage Textuel** | Preuve par citation | Présence de guillemets et extrait exact | $= 100\%$ | **100% (GO)** |
| **Porte 3 : Fact-Checking** | Rapprochement de données | Identification et rapprochement officiel | $\ge 90\%$ | **100% (GO)** |
| **Porte 4 : Neutralité** | Posture de tuteur | Absence de vocabulaire accusatoire + question réflexive | $= 100\%$ | **100% (GO)** |
| **Porte 5 : Latence Opérationnelle**| Vitesse de réponse (P95) | 95e percentile du temps de réponse | $< 8 000$ ms | **103.5 ms (GO)** |
| **Porte 6 : Traçabilité SQLite** | Journalisation des audits | Taux d'enregistrement en base locale | $= 100\%$ | **100% (GO)** |

* **Mesure Spécifique de Neutralité (Banc des Paires Miroirs) :**
  - Test sur 6 paires de textes symétriques traitant du même thème (dette, retraites, immigration, énergie, SMIC, IA).
  - Mesure de l'écart de traitement : **8.3 points d'écart moyen** (seuil de tolérance $\le 15$ points ➔ **Validé Neutre**).

---

## 4. Structure Idéale des Slides pour la Prochaine Soutenance (10 Slides Max)

* **Slide 1 — Titre & Vision :** *« Pédagogie de l'Esprit Critique : outiller le citoyen face aux discours sans devenir un censeur »*.
* **Slide 2 — Le Problème & La Persona :** Lucas, 20 ans, submergé par les tribunes virales anxiogènes.
* **Slide 3 — Notre Proposition de Valeur :** Décomposition en 5 blocs (Thèse, Pièges logiques, Fact-checking, Question ouverte, Limites).
* **Slide 4 — Démonstration Live (Vidéo/Direct) :** L'exemple du Chômage à 25% déconstruit en 2 secondes.
* **Slide 5 — Architecture Technique :** Schéma modulaire (Gemma 2 + Pydantic + Fact-checking Banque Mondiale + Catalogue 15 pièges).
* **Slide 6 — Données & Gouvernance :** Corpus de 45 textes calibrés, double annotation, split dev/test hermétique.
* **Slide 7 — Sécurité & Guardrails :** Zéro hallucination sur les chiffres, posture non-arbitre, validation stricte.
* **Slide 8 — Résultats Scientifiques :** Tableau des 6 Portes Go/No-Go (100% GO) + Test de neutralité (8.3 pts).
* **Slide 9 — Vision Industrielle (Scale-up) :** Déploiement vLLM GPU A10G, Cache Redis sémantique, coût à 0,0003 € par requête.
* **Slide 10 — Conclusion & Roadmap :** Intégration en milieu scolaire (ateliers EMI), partenariats d'éducation aux médias.
