# IALLM — Streamlit RAG PoC (documents internes juridiques)

Prototype **Streamlit** en Python qui permet :
1) d’uploader des documents internes (`.txt`, `.csv`, `.html`)
2) de les nettoyer, découper en chunks et vectoriser (embeddings)
3) de stocker ces embeddings dans une base vectorielle **Chroma** (persistante sur disque)
4) de poser des questions dans une interface chat et d’obtenir des réponses **basées uniquement sur les documents indexés** (RAG)

---

## 1) Fonctionnalités

### Page Documents
- Upload `.txt`, `.csv`, `.html`
- Sauvegarde des fichiers dans `data/uploads/`
- Pipeline automatique : parsing → nettoyage → chunking → embeddings → indexation Chroma
- Liste des documents existants + aperçu
- Suppression : supprime le fichier + supprime les chunks associés dans Chroma

### Page Chat (RAG)
- Chat utilisateur ↔ assistant
- Réponses basées sur retrieval + LLM
- Format strict pour faciliter le debug :
  - Réponse
  - Preuve (extrait cité)
  - Source (fichier + chunk)
- Affichage des sources utilisées (debug)
- Historique en mémoire via `st.session_state`

---

## 2) Stack et choix

- **Streamlit** : prototypage UI rapide (multi-pages)
- **OpenAI API** :
  - embeddings → indexation + recherche vectorielle
  - chat completions → génération de la réponse finale
- **ChromaDB** : base vectorielle locale persistante (`data/chroma/`)
- **Python 3.12+** + venv

Pourquoi Chroma ?
- simple à intégrer
- persistance locale (important en PoC)
- API claire (`upsert`, `query`, `delete`, `count`)

---

## 3) Architecture du projet

```txt
IALLM/
├─ app/
│  ├─ config.py        # Charge .env + settings globaux
│  ├─ llm.py           # Client OpenAI + tests embedding/chat
│  ├─ preprocess.py    # parse txt/csv/html + clean_text + chunk_text
│  ├─ indexer.py       # ingestion: parse -> chunk -> embed -> upsert
│  ├─ storage.py       # save/list/read/delete fichiers uploadés
│  └─ vectorstore.py   # accès Chroma (persistant)
│
├─ pages/
│  ├─ 1_Chat.py        # Chat RAG (réponse + preuve + source)
│  └─ 2_Documents.py   # Upload / liste / aperçu / suppression
│
├─ data/
│  ├─ uploads/         # fichiers uploadés (persistant)
│  └─ chroma/          # index Chroma (persistant)
│
├─ Home.py             # point d’entrée Streamlit (page d'accueil)
├─ requirements.txt    # dépendances
├─ .env.example        # exemple (sans secrets)
└─ .gitignore
```

---

## 4) Installation (phases pas à pas)
Phase 0 — Pré-requis

Python 3.12+ installé.

Vérifier :

python3 --version

Sur Ubuntu/Debian, si la venv ne marche pas :

sudo apt install python3.12-venv

## Phase 1 — Cloner le repo

git clone git@github.com:NicolasGarric/IALLM.git
cd IALLM

## Phase 2 — Créer et activer la venv

python3 -m venv .venv
source .venv/bin/activate

Vérifier :

which python
python --version
pip --version

## Phase 3 — Installer les dépendances

pip install -r requirements.txt

---

## 5) Configuration

Créer un fichier .env à la racine (ou copier .env.example) :

cp .env.example .env

Puis compléter .env :

OPENAI_API_KEY=...
LLM_MODEL=gpt-4o-mini
EMBED_MODEL=text-embedding-3-small
TOP_K=5
UPLOADS_DIR=data/uploads
CHROMA_DIR=data/chroma

Notes :

    Ne jamais commit .env (contient une clé secrète).

    TOP_K contrôle le nombre d’extraits récupérés pour construire le contexte.

---

## 6) Lancer l’application

Avec la venv activée :

streamlit run Home.py

Ouvre l’URL affichée (souvent http://localhost:8501).

---

## 7) Comment ça marche (RAG)

7.1 Ingestion (Documents → Index)

Quand un fichier est uploadé :

    Sauvegarde dans data/uploads/ (app/storage.py)

    Parsing selon le type :

        .txt → lecture + nettoyage

        .csv → conversion en texte ligne par ligne

        .html → extraction du texte

    Nettoyage du texte

    Découpage en chunks (avec overlap)

    Vectorisation (embeddings)

    Stockage dans Chroma : chunks + embeddings + métadonnées (source, chunk_id)

7.2 Question / Answering (Chat → Retrieval → Réponse)

    Embedding de la question

    Retrieval : Chroma retourne les TOP_K chunks les plus proches

    Construction du contexte (concaténation des chunks + tags source/chunk)

    Appel LLM avec contrainte “uniquement contexte”

    Sortie au format strict : Réponse / Preuve / Source

---

## 8) Choix techniques & compromis

    Streamlit : prototypage rapide sans framework front.

    Chroma : persistance locale et API simple.

    Embeddings : retrieval sémantique (recherche par sens, pas seulement mots-clés).

    Anti-hallucination : format strict + preuve citée + sources visibles. Si l’info manque : “Je ne sais pas…”.

    Limites : PDF non supporté (hors scope), historique non persisté (session uniquement).

---

## 9) Quick demo (2 minutes)

    Uploade un fichier .txt dans Documents.

    Va dans Chat et pose : “Quel est le préavis de résiliation ?”

    Vérifie que la réponse contient une preuve citée et une source (fichier + chunk).

---

## 10) Données et reset

    Uploads : data/uploads/

    Index Chroma : data/chroma/

Reset complet de l’index (supprime toute l’indexation) :

rm -rf data/chroma/*

---

## 11) Dépannage

    command not found: python : activer la venv source .venv/bin/activate

    ensurepip is not available : installer python3.12-venv

    “Je ne sais pas…” : vérifier que des documents sont indexés, augmenter TOP_K, regarder le debug des sources

---

## 12) Sécurité (PoC)

    Ne jamais commit .env (clé API).

    Les documents sont stockés localement dans data/uploads/ (PoC).

    En production : contrôle d’accès, chiffrement, audit logs, et séparation des environnements.
