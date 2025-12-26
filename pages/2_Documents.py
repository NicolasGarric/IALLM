import streamlit as st

from app.storage import save_upload, list_uploads, delete_upload, read_upload
from app.indexer import index_file
from app.vectorstore import delete_source, count_chunks

st.set_page_config(page_title="Documents", page_icon="📄", layout="wide")
st.title("📄 Gestion des documents")
st.caption("Formats supportés : .txt, .csv, .html")

# --- Upload ---
st.subheader("Uploader un document")
uploaded = st.file_uploader("Choisir un fichier", type=["txt", "csv", "html"])

if uploaded is not None:
    filename = uploaded.name
    raw = uploaded.getvalue()

    try:
        # 1) Sauvegarde sur disque
        save_upload(filename, raw)

        # 2) Indexation dans la base vectorielle
        with st.spinner("Indexation (nettoyage → découpage → embeddings → Chroma)..."):
            n_chunks = index_file(filename, raw)

        if n_chunks == 0:
            st.warning("Document vide (après nettoyage) : aucun chunk indexé.")
        else:
            st.success(f"✅ {filename} indexé : {n_chunks} chunk(s).")
            st.info(f"Total chunks en base : {count_chunks()}")

    except Exception as e:
        st.error(f"Erreur upload/indexation : {e}")

st.divider()

# --- Liste ---
st.subheader("Documents existants")
files = list_uploads()

if not files:
    st.write("Aucun document uploadé.")
else:
    for f in files:
        c1, c2, c3 = st.columns([5, 1, 1])

        with c1:
            st.markdown(f"**{f}**")

        with c2:
            if st.button("👁️ Aperçu", key=f"preview_{f}"):
                try:
                    raw = read_upload(f)
                    # Affiche seulement un extrait pour éviter les gros fichiers
                    preview = raw[:4000].decode("utf-8", errors="ignore")
                    st.code(preview)
                except Exception as e:
                    st.error(f"Erreur aperçu : {e}")

        with c3:
            if st.button("🗑️ Supprimer", key=f"delete_{f}"):
                try:
                    # 1) Supprimer de Chroma (chunks)
                    delete_source(f)

                    # 2) Supprimer le fichier
                    deleted = delete_upload(f)

                    if deleted:
                        st.success(f"Supprimé : {f}")
                    else:
                        st.warning(f"Fichier introuvable : {f}")

                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur suppression : {e}")

st.divider()
st.info(f"Chunks indexés dans Chroma : **{count_chunks()}**")
