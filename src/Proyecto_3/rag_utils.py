"""
rag_utils.py
────────────
Pipeline RAG: chunking, embeddings, FAISS, búsqueda semántica.
Carga datos desde MongoDB (musica.canciones).
"""

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient

# ── Configuración ─────────────────────────────────────────────────────────────
EMBED_MODEL  = "paraphrase-multilingual-MiniLM-L12-v2"
CACHE_DIR    = os.path.join(os.path.dirname(__file__), "..", "..", "data", "embeddings_cache")
EMBED_CACHE  = os.path.join(CACHE_DIR, "embeddings.npy")
CHUNKS_CACHE = os.path.join(CACHE_DIR, "chunks.pkl")

MONGO_URI  = "mongodb://localhost:27017"
MONGO_DB   = "musica"
MONGO_COL  = "canciones"
GENEROS    = ["Rock", "Hip-Hop", "Metal"]

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


# ── Carga desde MongoDB ───────────────────────────────────────────────────────

def cargar_desde_mongo():
    """
    Carga las canciones de los géneros objetivo desde MongoDB.
    Retorna una lista de dicts con los campos necesarios.
    """
    client = MongoClient(MONGO_URI)
    col    = client[MONGO_DB][MONGO_COL]

    canciones = list(col.find(
        {"Genre": {"$in": GENEROS}},
        {"Song": 1, "Artist": 1, "Genre": 1, "Song year": 1, "Lyrics": 1, "_id": 0}
    ))

    client.close()
    print(f"✓ {len(canciones)} canciones cargadas desde MongoDB")
    return canciones


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_por_cancion(canciones):
    """
    Estrategia 1: cada canción completa es un chunk.
    Acepta lista de dicts desde MongoDB.
    """
    chunks = []
    for c in canciones:
        texto = str(c.get("Lyrics") or "")
        if len(texto.strip()) < 50:
            continue
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
    """
    chunks = []
    for c in canciones:
        texto   = str(c.get("Lyrics") or "")
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
    Si chunks es None, carga automáticamente desde MongoDB.
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
            canciones = cargar_desde_mongo()
            chunks    = chunk_por_cancion(canciones)

        print(f"Generando embeddings para {len(chunks)} chunks...")
        model  = _get_model()
        textos = [c["texto"] for c in chunks]
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
    print(f"Índice FAISS listo con {_index.ntotal} vectores.")
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


# ── Estadísticas del corpus en Mongo ─────────────────────────────────────────

def stats_corpus():
    """Retorna estadísticas del corpus desde MongoDB."""
    client = MongoClient(MONGO_URI)
    col    = client[MONGO_DB][MONGO_COL]

    stats = {}
    for genero in GENEROS:
        stats[genero] = col.count_documents({"Genre": genero})
    stats["total"] = col.count_documents({"Genre": {"$in": GENEROS}})

    client.close()
    return stats