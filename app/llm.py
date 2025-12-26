# app/llm.py
from openai import OpenAI
from app.config import settings

def get_client() -> OpenAI:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY manquante dans le dossier .env")
    return OpenAI(api_key=settings.openai_api_key)

def test_embedding() -> int:
    client = get_client()
    resp = client.embeddings.create(
        model=settings.embed_model,
        input="Test embedding: contrat de prestation de services.",
    )
    # Taille du vecteur -- test
    return len(resp.data[0].embedding)

def test_chat() -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0,
        messages=[
            {"role": "system", "content": "Réponds en une phrase."},
            {"role": "user", "content": "Dis simplement bonjour."},
        ],
    )
    return resp.choices[0].message.content or ""
