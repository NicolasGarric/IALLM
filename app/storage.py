# app/storage.py
import os
from app.config import settings

IGNORED_FILES = {".gitkeep"}

def _safe_filename(filename: str) -> str:
    safe = os.path.basename(filename or "").strip()
    if not safe:
        raise ValueError("Nom de fichier invalide.")
    return safe

def save_upload(filename: str, raw: bytes) -> str:
    os.makedirs(settings.uploads_dir, exist_ok=True)

    safe_name = _safe_filename(filename)
    path = os.path.join(settings.uploads_dir, safe_name)

    with open(path, "wb") as f:
        f.write(raw)

    return path

def list_uploads() -> list[str]:
    if not os.path.exists(settings.uploads_dir):
        return []

    files = []
    for name in os.listdir(settings.uploads_dir):
        if name in IGNORED_FILES:
            continue
        full = os.path.join(settings.uploads_dir, name)
        if os.path.isfile(full):
            files.append(name)

    return sorted(files)

def delete_upload(filename: str) -> bool:
    safe_name = _safe_filename(filename)
    path = os.path.join(settings.uploads_dir, safe_name)

    if os.path.exists(path) and os.path.isfile(path):
        os.remove(path)
        return True

    return False

def read_upload(filename: str) -> bytes:
    safe_name = _safe_filename(filename)
    path = os.path.join(settings.uploads_dir, safe_name)

    with open(path, "rb") as f:
        return f.read()
