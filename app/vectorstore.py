# app/vectorstore.py
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings

COLLECTION_NAME = "legal_docs"

def _ensure_dirs() -> None:
    os.makedirs(settings.uploads_dir, exist_ok=True)
    os.makedirs(settings.chroma_dir, exist_ok=True)

def get_collection():
    """
    Ouvre (ou crée) une collection Chroma persistante sur disque.
    """
    _ensure_dirs()
    client = chromadb.PersistentClient(
        path=settings.chroma_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(name=COLLECTION_NAME)

def upsert_chunks(ids: list[str], documents: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
    """
    Ajoute / met à jour des chunks dans Chroma.
    """
    col = get_collection()
    col.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

def query_chunks(query_embedding: list[float], top_k: int):
    """
    Recherche les top_k chunks les plus proches d'un embedding de question.
    """
    col = get_collection()
    return col.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

def delete_source(source_name: str) -> None:
    """
    Supprime tous les chunks dont la metadata source == source_name.
    """
    col = get_collection()
    col.delete(where={"source": source_name})

def count_chunks() -> int:
    col = get_collection()
    return col.count()
