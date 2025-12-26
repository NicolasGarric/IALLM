# app/preprocess.py
import re
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

def clean_text(text: str) -> str:
    """
    Nettoyage simple :
    - supprime caractères nuls
    - normalise les espaces
    - réduit les sauts de ligne multiples
    """
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def parse_txt(raw: bytes) -> str:
    return clean_text(raw.decode("utf-8", errors="ignore"))

def parse_html(raw: bytes) -> str:
    html = raw.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    return clean_text(text)

def parse_csv(raw: bytes) -> str:
    df = pd.read_csv(BytesIO(raw), dtype=str, keep_default_na=False)
    lines = []
    for _, row in df.iterrows():
        line = " | ".join([str(v) for v in row.values if str(v).strip()])
        if line.strip():
            lines.append(line)
    return clean_text("\n".join(lines))

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    """
    Découpe en morceaux :
    - chunk_size : taille max
    - overlap : chevauchement pour ne pas couper une info importante
    """
    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == n:
            break

        start = max(0, end - overlap)

    return chunks
