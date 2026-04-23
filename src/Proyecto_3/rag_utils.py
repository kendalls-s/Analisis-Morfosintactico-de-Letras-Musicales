"""
rag_utils.py
────────────
Pipeline RAG: chunking, embeddings, FAISS, búsqueda semántica.
Carga datos desde CSV (data/raw/) y guarda procesado en data/processed/.
"""

import os
import re
import pickle
import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

# ── Configuración ─────────────────────────────────────────────────────────────
EMBED_MODEL   = "paraphrase-multilingual-MiniLM-L12-v2"

BASE_DIR      = os.path.join(os.path.dirname(__file__), "..", "..")
RAW_CSV       = os.path.join(BASE_DIR, "data", "raw", "spotify_dataset.csv")
PROCESSED_CSV = os.path.join(BASE_DIR, "data", "processed", "canciones_limpias.csv")
CACHE_DIR     = os.path.join(BASE_DIR, "data", "embeddings_cache")
EMBED_CACHE   = os.path.join(CACHE_DIR, "embeddings.npy")
CHUNKS_CACHE  = os.path.join(CACHE_DIR, "chunks.pkl")

GENEROS      = ["Rock", "Hip-Hop", "Metal"]
RANDOM_STATE = 42   # seed global — cambiar aquí afecta todo el pipeline

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "data", "processed"), exist_ok=True)

_model  = None
_index  = None
_chunks = None


def _get_model():
    global _model
    if _model is None:
        print("Cargando modelo de embeddings...")
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


# ── Limpieza de texto ─────────────────────────────────────────────────────────

def limpiar_texto(texto):
    if not isinstance(texto, str) or texto.strip().lower() in ("nan", "none", ""):
        return ""
    texto = re.sub(r'\[.*?\]', '', texto)       # quitar [chorus], [verse], etc.
    texto = re.sub(r'[^a-zA-Z\s]', '', texto)   # solo letras y espacios
    texto = re.sub(r'[ \t]+', ' ', texto)        # colapsar espacios/tabs (no \n)
    texto = texto.strip()
    return texto


# ── Carga desde CSV ───────────────────────────────────────────────────────────
def cargar_desde_csv(raw_path=None, save_processed=True, balancear=True):
    path = raw_path or RAW_CSV
    print(f"Leyendo CSV desde: {path}")
    df = pd.read_csv(path)
    print(f"  → {len(df)} filas totales en el CSV")

    # ── FIX 0: detectar y renombrar columna Genre si tiene otro nombre ──────
    col_map = {c: c for c in df.columns}
    rename = {}
    for col in df.columns:
        normalized = col.strip().lower().replace(" ", "_")
        if normalized == "genre" and col != "Genre":
            rename[col] = "Genre"
        elif normalized in ("track_genre", "song_genre", "music_genre") and "Genre" not in df.columns:
            rename[col] = "Genre"
        elif col.strip() != col:          # leading/trailing whitespace in header
            rename[col] = col.strip()
    if rename:
        print(f"  → Renombrando columnas: {rename}")
        df = df.rename(columns=rename)

    print(f"  → Columnas detectadas: {df.columns.tolist()}")

    if "Genre" not in df.columns:
        raise ValueError(
            f"No se encontró columna 'Genre'. Columnas disponibles: {df.columns.tolist()}"
        )

    # ── FIX 1: limpiar columna Genre ────────────────────────────────────────
    df["Genre"] = df["Genre"].astype(str).str.strip()
    print("  → Géneros únicos detectados:", df["Genre"].unique().tolist())

    # ── FIX 2: filtro case-insensitive ──────────────────────────────────────
    generos_lower = [g.lower() for g in GENEROS]
    df = df[df["Genre"].str.lower().isin(generos_lower)].reset_index(drop=True)
    print(f"  → {len(df)} canciones tras filtrar géneros: {GENEROS}")

    if df.empty:
        raise ValueError(
            f"Ninguna fila coincide con los géneros {GENEROS}. "
            f"Revisá los valores únicos de Genre en tu CSV."
        )

    # ── FIX 3: eliminar duplicados ───────────────────────────────────────────
    # Detectar columna Song con nombre alternativo
    song_col   = next((c for c in df.columns if c.strip().lower() in ("song", "track", "track_name", "title")), None)
    artist_col = next((c for c in df.columns if c.strip().lower() in ("artist", "artist_name", "artists")), None)

    if song_col and artist_col:
        antes = len(df)
        df = df.drop_duplicates(subset=[artist_col, song_col]).reset_index(drop=True)
        print(f"  → {len(df)} canciones únicas (eliminados {antes - len(df)} duplicados)")
    else:
        print(f"  ⚠ No se encontraron columnas Artist/Song para deduplicar. "
              f"Columnas: {df.columns.tolist()}")

    # ── FIX 4: limpiar Lyrics ────────────────────────────────────────────────
    lyrics_col = next((c for c in df.columns if c.strip().lower() in ("lyrics", "lyric", "text")), None)
    if lyrics_col and lyrics_col != "Lyrics":
        df = df.rename(columns={lyrics_col: "Lyrics"})
    if "Lyrics" not in df.columns:
        raise ValueError(f"No se encontró columna 'Lyrics'. Columnas: {df.columns.tolist()}")

    df["Lyrics"] = df["Lyrics"].astype(str).apply(limpiar_texto)

    # ── FIX 5: descartar lyrics vacías ──────────────────────────────────────
    antes = len(df)
    df = df[df["Lyrics"].str.len() >= 50].reset_index(drop=True)
    print(f"  → {len(df)} canciones con lyrics válidas "
          f"(descartadas {antes - len(df)} demasiado cortas/vacías)")

    if df.empty:
        raise ValueError("Todas las lyrics quedaron vacías tras la limpieza.")

    # ── Balanceo ─────────────────────────────────────────────────────────────
    if balancear:
        min_canciones = df["Genre"].value_counts().min()
        partes = []
        for genero, grupo in df.groupby("Genre"):
            partes.append(grupo.sample(min_canciones, random_state=RANDOM_STATE))
        df = pd.concat(partes).reset_index(drop=True)
        print(f"  → Dataset balanceado: {min_canciones} canciones por género "
              f"(seed={RANDOM_STATE})")

    print("  → Conteo final por género:")
    print(df["Genre"].value_counts().to_string())
    print(f"  → Total: {len(df)} canciones")

    if save_processed:
        df.to_csv(PROCESSED_CSV, index=False)
        print(f"✓ CSV procesado guardado en: {PROCESSED_CSV}")

    return df

# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_por_cancion(canciones):
    """
    Estrategia 1: cada canción completa es un chunk.
    Acepta DataFrame o lista de dicts.
    """
    if isinstance(canciones, pd.DataFrame):
        canciones = canciones.to_dict(orient="records")

    chunks = []
    vistos = set()  # evitar chunks duplicados

    for c in canciones:
        texto = str(c.get("Lyrics") or "").strip()
        if len(texto) < 50:
            continue

        clave = (str(c.get("Artist", "")).lower(), str(c.get("Song", "")).lower())
        if clave in vistos:
            continue
        vistos.add(clave)

        chunks.append({
            "texto":      texto[:1500],
            "song":       str(c.get("Song", "")),
            "artist":     str(c.get("Artist", "")),
            "genre":      str(c.get("Genre", "")),
            "year":       int(c.get("Song year", 0) or 0),
            "estrategia": "cancion_completa",
        })
    return chunks


def chunk_por_estrofa(canciones, min_len=40):
    """
    Estrategia 2: cada estrofa es un chunk.
    Acepta DataFrame o lista de dicts.
    """
    if isinstance(canciones, pd.DataFrame):
        canciones = canciones.to_dict(orient="records")

    chunks = []
    for c in canciones:
        texto    = str(c.get("Lyrics") or "").strip()
        estrofas = [e.strip() for e in texto.split("\n\n") if len(e.strip()) >= min_len]
        for estrofa in estrofas:
            chunks.append({
                "texto":      estrofa[:800],
                "song":       str(c.get("Song", "")),
                "artist":     str(c.get("Artist", "")),
                "genre":      str(c.get("Genre", "")),
                "year":       int(c.get("Song year", 0) or 0),
                "estrategia": "estrofa",
            })
    return chunks


# ── Embeddings y FAISS ────────────────────────────────────────────────────────

def construir_indice(chunks=None, forzar=False):
    """
    Genera embeddings y construye índice FAISS.
    Si chunks es None, carga automáticamente desde CSV.
    Cachea en disco para no recalcular.
    """
    global _index, _chunks

    if not forzar and os.path.exists(EMBED_CACHE) and os.path.exists(CHUNKS_CACHE):
        print("Cargando embeddings desde caché...")
        embeddings = np.load(EMBED_CACHE)
        with open(CHUNKS_CACHE, "rb") as f:
            _chunks = pickle.load(f)
    else:
        if chunks is None:
            df     = cargar_desde_csv()
            chunks = chunk_por_cancion(df)

        print(f"Generando embeddings para {len(chunks)} chunks...")
        model      = _get_model()
        textos     = [c["texto"] for c in chunks]
        embeddings = model.encode(
            textos, show_progress_bar=True,
            batch_size=32, convert_to_numpy=True
        )
        np.save(EMBED_CACHE, embeddings)
        with open(CHUNKS_CACHE, "wb") as f:
            pickle.dump(chunks, f)
        _chunks = chunks
        print("Embeddings guardados en caché.")

    # Normalizar para búsqueda por coseno
    faiss.normalize_L2(embeddings)
    dim    = embeddings.shape[1]
    _index = faiss.IndexFlatIP(dim)
    _index.add(embeddings)
    print(f"✓ Índice FAISS listo con {_index.ntotal} vectores.")
    return _index, _chunks


def buscar_chunks(query, top_k=5, filtro_genero=None):
    """
    Busca los top_k chunks más relevantes para la query.
    """
    global _index, _chunks
    if _index is None or _chunks is None:
        raise RuntimeError("Llama primero a construir_indice().")

    model = _get_model()
    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)

    k       = min(top_k * 3, len(_chunks))
    scores, indices = _index.search(q_emb, k)

    resultados = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        chunk = _chunks[idx]
        if filtro_genero and chunk["genre"].lower() != filtro_genero.lower():
            continue
        resultados.append({**chunk, "score": float(score)})
        if len(resultados) >= top_k:
            break

    return resultados


# ── Estadísticas del corpus ───────────────────────────────────────────────────

def stats_corpus(df=None):
    """Retorna estadísticas del corpus. Si no se pasa df, lo carga desde CSV."""
    if df is None:
        df = cargar_desde_csv(save_processed=False)

    stats = {genero: int((df["Genre"] == genero).sum()) for genero in GENEROS}
    stats["total"] = len(df)
    return stats