import streamlit as st

from app.config import settings
from app.vectorstore import count_chunks
from app.storage import list_uploads

st.set_page_config(
    page_title="IALLM — RAG PoC",
    page_icon="🧠",
    layout="wide",
)

st.title("IALLM — RAG PoC (documents internes)")
st.write(
    "Ce prototype permet d’uploader des documents internes (.txt/.csv/.html), "
    "de les indexer et de poser des questions via un chat. "
    "Les réponses sont basées uniquement sur les documents indexés."
)

st.divider()

# État du système
uploads = list_uploads()
chunks = count_chunks()

c1, c2, c3 = st.columns(3)
c1.metric("Documents uploadés", len(uploads))
c2.metric("Chunks indexés", chunks)
c3.metric("TOP_K (retrieval)", settings.top_k)

st.divider()

st.subheader("Démarrage rapide")
st.markdown(
    """
1. Ouvre la page **Documents** et uploade un fichier.
2. Vérifie le message d’indexation (chunks créés).
3. Ouvre la page **Chat** et pose une question.
4. Consulte **Sources (debug)** pour vérifier les extraits utilisés.
"""
)

st.subheader("Règle anti-hallucination")
st.markdown(
    """
Le chat doit répondre uniquement à partir des extraits récupérés dans la base vectorielle.
Si l’information n’est pas présente dans le contexte, la réponse doit être :

**Je ne sais pas d’après les documents fournis.**

Le format de sortie est strict :
- Réponse
- Preuve (extrait cité)
- Source (fichier + chunk)
"""
)

st.divider()

st.subheader("Documents récents")
if not uploads:
    st.info("Aucun document uploadé. Va dans Documents pour commencer.")
else:
    for name in uploads[:10]:
        st.write(f"- {name}")
    if len(uploads) > 10:
        st.caption(f"{len(uploads) - 10} autres…")

st.divider()
st.caption("Données locales : data/uploads (fichiers) et data/chroma (index vectoriel).")
