# app/indexer.py
import os
from app.config import settings
from app.llm import get_client
from app.preprocess import parse_txt, parse_csv, parse_html, chunk_text
from app.vectorstore import upsert_chunks

# Paramètres simples (on pourra les déplacer dans Settings plus tard)
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

def _parse_file_to_text(filename: str, raw: bytes) -> str:
    """
    Convertit le contenu brut (bytes) en texte propre selon l'extension.
    Supporte : .txt, .csv, .html
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return parse_txt(raw)
    if ext == ".csv":
        return parse_csv(raw)
    if ext in [".html", ".htm"]:
        return parse_html(raw)

    raise ValueError(f"Format non supporté : {ext} (supportés: .txt, .csv, .html)")

def index_file(filename: str, raw: bytes) -> int:
    """
    Pipeline complet :
    1) parse (txt/csv/html) -> texte
    2) chunking -> liste de chunks
    3) embeddings -> vecteurs
    4) upsert -> stockage dans Chroma

    Retourne : nombre de chunks indexés
    """
    # 1) Parse -> texte
    text = _parse_file_to_text(filename, raw)

    # 2) Chunking
    chunks = chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    if not chunks:
        return 0

    # 3) Embeddings (en batch)
    client = get_client()
    resp = client.embeddings.create(
        model=settings.embed_model,
        input=chunks,
    )
    embeddings = [d.embedding for d in resp.data]

    # 4) Upsert dans Chroma
    ids = [f"{filename}::chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename, "chunk_id": i} for i in range(len(chunks))]

    upsert_chunks(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)
