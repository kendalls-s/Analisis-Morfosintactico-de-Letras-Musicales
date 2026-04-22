"""
rag_utils.py
────────────
Pipeline RAG: chunking, embeddings, FAISS, búsqueda semántica.
"""

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ── Configuración ─────────────────────────────────────────────────────────────
EMBED_MODEL   = "paraphrase-multilingual-MiniLM-L12-v2"
CACHE_DIR     = os.path.join(os.path.dirname(__file__), "..", "data", "embeddings_cache")
EMBED_CACHE   = os.path.join(CACHE_DIR, "embeddings.npy")
CHUNKS_CACHE  = os.path.join(CACHE_DIR, "chunks.pkl")

os.makedirs(CACHE_DIR, exist_ok=True)

_model  = None
_index  = None
_chunks = None


def _get_model():
    global _model
    if _model is None:
        print("Cargando modelo de embeddings...")
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_por_cancion(df):
    """
    Estrategia 1: cada canción completa es un chunk.
    Retorna lista de dicts con texto y metadatos.
    """
    chunks = []
    for _, row in df.iterrows():
        texto = str(row.get("Lyrics") or row.get("Clean_Lyrics") or "")
        if len(texto.strip()) < 50:
            continue
        chunks.append({
            "texto":   texto[:1500],
            "song":    str(row.get("Song", "")),
            "artist":  str(row.get("Artist", "")),
            "genre":   str(row.get("Genre", "")),
            "year":    int(row.get("Song year", 0) or 0),
            "estrategia": "cancion_completa",
        })
    return chunks


def chunk_por_estrofa(df, min_len=40):
    """
    Estrategia 2: cada estrofa (separada por línea vacía) es un chunk.
    Retorna lista de dicts con texto y metadatos.
    """
    chunks = []
    for _, row in df.iterrows():
        texto = str(row.get("Lyrics") or "")
        estrofas = [e.strip() for e in texto.split("\n\n") if len(e.strip()) >= min_len]
        for estrofa in estrofas:
            chunks.append({
                "texto":   estrofa[:800],
                "song":    str(row.get("Song", "")),
                "artist":  str(row.get("Artist", "")),
                "genre":   str(row.get("Genre", "")),
                "year":    int(row.get("Song year", 0) or 0),
                "estrategia": "estrofa",
            })
    return chunks


# ── Embeddings y FAISS ────────────────────────────────────────────────────────

def construir_indice(chunks, forzar=False):
    """
    Genera embeddings y construye índice FAISS.
    Cachea en disco para no recalcular.
    """
    global _index, _chunks

    if not forzar and os.path.exists(EMBED_CACHE) and os.path.exists(CHUNKS_CACHE):
        print("Cargando embeddings desde caché...")
        embeddings = np.load(EMBED_CACHE)
        with open(CHUNKS_CACHE, "rb") as f:
            _chunks = pickle.load(f)
    else:
        print(f"Generando embeddings para {len(chunks)} chunks...")
        model = _get_model()
        textos = [c["texto"] for c in chunks]
        embeddings = model.encode(textos, show_progress_bar=True,
                                  batch_size=32, convert_to_numpy=True)
        np.save(EMBED_CACHE, embeddings)
        with open(CHUNKS_CACHE, "wb") as f:
            pickle.dump(chunks, f)
        _chunks = chunks
        print("Embeddings guardados en caché.")

    # Normalizar para búsqueda por coseno
    faiss.normalize_L2(embeddings)
    dim = embeddings.shape[1]
    _index = faiss.IndexFlatIP(dim)
    _index.add(embeddings)
    print(f"Índice FAISS construido con {_index.ntotal} vectores.")
    return _index, _chunks


def buscar_chunks(query, top_k=5, filtro_genero=None):
    """
    Busca los top_k chunks más relevantes para la query.
    Opcionalmente filtra por género.
    """
    global _index, _chunks
    if _index is None or _chunks is None:
        raise RuntimeError("Llama primero a construir_indice().")

    model  = _get_model()
    q_emb  = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)

    k      = min(top_k * 3, len(_chunks))
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
