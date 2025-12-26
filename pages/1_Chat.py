import streamlit as st

from app.config import settings
from app.llm import get_client
from app.vectorstore import query_chunks, count_chunks

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")
st.title("💬 Chat (RAG)")
st.caption("Réponses basées uniquement sur les documents indexés (.txt/.csv/.html).")

# --- Session state : historique chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []  # list[{"role": "...", "content": "..."}]

# --- Barre d'actions ---
c1, c2 = st.columns([1, 2])
with c1:
    if st.button("🧹 Nouvelle conversation"):
        st.session_state.messages = []
        st.rerun()
with c2:
    st.info(f"Chunks indexés dans Chroma : **{count_chunks()}** | top_k : **{settings.top_k}**")

# --- Affichage historique ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input utilisateur ---
question = st.chat_input("Pose ta question (ex: Quel est le préavis de résiliation ?)")

def build_context(docs: list[str], metas: list[dict]) -> str:
    """
    Construit un contexte lisible pour le LLM + des repères de sources.
    """
    parts = []
    for i, (doc, md) in enumerate(zip(docs, metas), start=1):
        src = md.get("source", "unknown")
        cid = md.get("chunk_id", "?")
        parts.append(f"[Source {i} | {src} | chunk {cid}]\n{doc}")
    return "\n\n---\n\n".join(parts)

def answer_with_rag(user_question: str) -> tuple[str, dict]:
    """
    Retourne (réponse, debug_sources).
    debug_sources contient docs/metas/distances pour affichage.
    """
    client = get_client()

    # 1) Embedding de la question
    q_emb = client.embeddings.create(
        model=settings.embed_model,
        input=user_question
    ).data[0].embedding

    # 2) Retrieval (Chroma)
    res = query_chunks(q_emb, top_k=settings.top_k)

    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]

    best_source = ""
    if metas:
        src = metas[0].get("source", "unknown")
        cid = metas[0].get("chunk_id", "?")
        best_source = f"{src} | chunk {cid}"

    dists = (res.get("distances") or [[]])[0]

    # Si rien trouvé / base vide
    if not docs:
        return "Je ne sais pas d’après les documents fournis.", {"docs": [], "metas": [], "dists": []}

    context = build_context(docs, metas)

    # 3) Appel LLM avec règle stricte (anti-hallucination)
    system_prompt = (
        "Tu es un assistant interne. RÈGLE ABSOLUE : tu réponds uniquement à partir du CONTEXTE fourni. "
        "Tu dois produire une réponse au format EXACT suivant (3 lignes) :\n"
        "Réponse : <ta réponse>\n"
        "Preuve (extrait) : \"<citation exacte copiée/collée depuis le contexte>\"\n"
        "Source : <nom_fichier> | chunk <num_chunk>\n"
        "\n"
        "CONTRAINTES :\n"
        "- La 'Preuve (extrait)' doit être une citation exacte provenant du contexte.\n"
        "- La 'Source' doit correspondre exactement à la preuve (nom_fichier + chunk).\n"
        "- Si la réponse n'est pas dans le contexte ou si tu ne peux pas citer une preuve exacte, répond EXACTEMENT :\n"
        "Je ne sais pas d’après les documents fournis."
    )

    user_prompt = (
        f"QUESTION:\n{user_question}\n\n"
        f"MEILLEURE SOURCE (si utile): {best_source}\n\n"
        f"CONTEXTE (extraits internes):\n{context}\n\n"
        "Réponds en respectant STRICTEMENT le format demandé."
    )

    resp = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer = resp.choices[0].message.content or ""

    # Fallback si le modèle ne respecte pas le format strict
    required = ["Réponse :", "Preuve (extrait) :", "Source :"]
    if not all(x in answer for x in required):
        answer = "Je ne sais pas d’après les documents fournis."

    return answer, {"docs": docs, "metas": metas, "dists": dists}

# --- Traitement d'une nouvelle question ---
if question:
    # Affiche le message user
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Réponse assistant
    with st.chat_message("assistant"):
        with st.spinner("Recherche dans les documents + génération..."):
            answer, dbg = answer_with_rag(question)

        st.markdown(answer)

        # Debug : sources + distances (preuve RAG)
        with st.expander("🔎 Sources utilisées (debug)"):
            if not dbg["docs"]:
                st.write("Aucune source trouvée.")
            else:
                for doc, md, dist in zip(dbg["docs"], dbg["metas"], dbg["dists"]):
                    st.write(f"- source: **{md.get('source')}** | chunk: **{md.get('chunk_id')}** | distance: **{round(dist, 4)}**")
                    st.code(doc[:2000])

    st.session_state.messages.append({"role": "assistant", "content": answer})
