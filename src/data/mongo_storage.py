"""
mongo_storage.py
────────────────
Capa de persistencia en MongoDB para canciones y sus métricas derivadas.
Estructura de documento:

{
  "_id":             ObjectId,
  "Song":            str,
  "Artist":          str,
  "Genre":           str,
  "Song year":       int,
  "Lyrics":          str,
  "Language":        str,
  "Source":          str,       # siempre "Genius"
  "Url":             str,
  "collection_date": datetime,
  "pos_tags":        { "nltk": [...], "spacy": [...] } | null,
  "embeddings":      { "word2vec_avg": [...], "beto_cls": [...] } | null,
  "metricas":        { ... } | null
}
"""

from datetime import datetime, timezone

from bson import ObjectId
from pymongo import MongoClient, UpdateOne

# ── Configuración por defecto ─────────────────────────────────────────────────

_DEFAULT_URI = "mongodb://localhost:27017"
_DEFAULT_DB  = "musica"
_DEFAULT_COL = "canciones"

# ── Conexión ──────────────────────────────────────────────────────────────────

def get_collection(
    uri: str = _DEFAULT_URI,
    db:  str = _DEFAULT_DB,
    col: str = _DEFAULT_COL,
):
    """Retorna el objeto Collection de PyMongo."""
    client = MongoClient(uri)
    return client[db][col]


_default_collection = None


def _get_default_collection():
    global _default_collection
    if _default_collection is None:
        _default_collection = get_collection()
    return _default_collection


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_object_id(value) -> ObjectId | None:
    """Convierte value a ObjectId; retorna None si no es posible."""
    try:
        return ObjectId(value)
    except Exception:
        return None


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)

def insertar_canciones_kag(canciones: list[dict], collection=None) -> dict:
    """
    Inserta o actualiza una lista de canciones en MongoDB.

    Cada elemento de `canciones` debe tener al menos:
        Song, Artist, Genre, Song year, Lyrics, Language, Url

    Usa upsert con clave (Song + Artist) para evitar duplicados.

    Retorna
    -------
    dict con claves "insertados" y "actualizados".
    """
    col = collection if collection is not None else _get_default_collection()
    operaciones = []
    now         = _now_utc()

    for c in canciones:
        # Normalizar año a entero cuando sea posible
        try:
            anio = int(c.get("Song year") or c.get("Año") or 0)
        except (ValueError, TypeError):
            anio = 0

        doc = {
            "_id":             ObjectId(),
            "Song":            c.get("Song")    or c.get("Nombre"),
            "Artist":          c.get("Artist")  or c.get("Artista"),
            "Genre":           c.get("Genre")   or c.get("Género"),
            "Song year":       anio,
            "Lyrics":          c.get("Lyrics")  or c.get("Letra"),
            "Language":        c.get("Language") or c.get("Idioma", "n/a"),
            "Source":          "kaggle",
            "Url":             c.get("Url")     or c.get("URL"),
            "collection_date": now,
            "pos_tags":        None,
            "embeddings":      None,
            "metricas":        None,
        }

        operaciones.append(
            UpdateOne(
                {"Song": doc["Song"], "Artist": doc["Artist"]},
                {"$setOnInsert": doc},
                upsert=True,
            )
        )

    if not operaciones:
        return {"insertados": 0, "actualizados": 0}

    resultado = col.bulk_write(operaciones, ordered=False)
    return {
        "insertados":   resultado.upserted_count,
        "actualizados": resultado.matched_count,
    }

# ── Inserción / Upsert ────────────────────────────────────────────────────────

def insertar_canciones(canciones: list[dict], collection=None) -> dict:
    """
    Inserta o actualiza una lista de canciones en MongoDB.

    Cada elemento de `canciones` debe tener al menos:
        Song, Artist, Genre, Song year, Lyrics, Language, Url

    Usa upsert con clave (Song + Artist) para evitar duplicados.

    Retorna
    -------
    dict con claves "insertados" y "actualizados".
    """
    col = collection if collection is not None else _get_default_collection()
    operaciones = []
    now         = _now_utc()

    for c in canciones:
        # Normalizar año a entero cuando sea posible
        try:
            anio = int(c.get("Song year") or c.get("Año") or 0)
        except (ValueError, TypeError):
            anio = 0

        doc = {
            "_id":             ObjectId(),
            "Song":            c.get("Song")    or c.get("Nombre"),
            "Artist":          c.get("Artist")  or c.get("Artista"),
            "Genre":           c.get("Genre")   or c.get("Género"),
            "Song year":       anio,
            "Lyrics":          c.get("Lyrics")  or c.get("Letra"),
            "Language":        c.get("Language") or c.get("Idioma", "n/a"),
            "Source":          "Genius",
            "Url":             c.get("Url")     or c.get("URL"),
            "collection_date": now,
            "pos_tags":        None,
            "embeddings":      None,
            "metricas":        None,
        }

        operaciones.append(
            UpdateOne(
                {"Song": doc["Song"], "Artist": doc["Artist"]},
                {"$setOnInsert": doc},
                upsert=True,
            )
        )

    if not operaciones:
        return {"insertados": 0, "actualizados": 0}

    resultado = col.bulk_write(operaciones, ordered=False)
    return {
        "insertados":   resultado.upserted_count,
        "actualizados": resultado.matched_count,
    }


# ── Actualización de campos derivados ────────────────────────────────────────

def guardar_pos_tags(
    song_id,
    nltk_tags:  list,
    spacy_tags: list,
    collection=None,
) -> bool:
    """Guarda los POS-tags de NLTK y spaCy para una canción."""
    col = collection or _get_default_collection()
    res = col.update_one(
        {"_id": _to_object_id(song_id)},
        {"$set": {"pos_tags": {"nltk": nltk_tags, "spacy": spacy_tags}}},
    )
    return res.modified_count > 0


def guardar_embeddings(
    song_id,
    word2vec_avg: list,
    beto_cls:     list,
    collection=None,
) -> bool:
    """Guarda los vectores de embeddings para una canción."""
    col = collection or _get_default_collection()
    res = col.update_one(
        {"_id": _to_object_id(song_id)},
        {"$set": {"embeddings": {"word2vec_avg": word2vec_avg, "beto_cls": beto_cls}}},
    )
    return res.modified_count > 0


def guardar_metricas(
    song_id,
    num_palabras:            int,
    vocab_unico:             int,
    n_sustantivos:           int,
    n_verbos:                int,
    n_adjetivos:             int,
    n_adverbios:             int,
    n_pronombres:            int,
    n_propios:               int,
    n_auxiliares:            int,
    n_interjecciones:        int,
    n_numerales:             int,
    densidad_lexica:         float,
    ttr:                     float,
    ratio_sustantivos_verbos: float,
    ratio_adj_sust:          float,
    ratio_adv_verb:          float,
    ratio_pron_sust:         float,
    ratio_func_cont:         float,
    collection=None,
) -> bool:
    """Guarda las métricas morfosintácticas de una canción."""
    col = collection or _get_default_collection()
    res = col.update_one(
        {"_id": _to_object_id(song_id)},
        {"$set": {
            "metricas": {
                "num_palabras":              num_palabras,
                "vocab_unico":               vocab_unico,
                "n_sustantivos":             n_sustantivos,
                "n_verbos":                  n_verbos,
                "n_adjetivos":               n_adjetivos,
                "n_adverbios":               n_adverbios,
                "n_pronombres":              n_pronombres,
                "n_propios":                 n_propios,
                "n_auxiliares":              n_auxiliares,
                "n_interjecciones":          n_interjecciones,
                "n_numerales":               n_numerales,
                "densidad_lexica":           densidad_lexica,
                "ttr":                       ttr,
                "ratio_sustantivos_verbos":  ratio_sustantivos_verbos,
                "ratio_adj_sust":            ratio_adj_sust,
                "ratio_adv_verb":            ratio_adv_verb,
                "ratio_pron_sust":           ratio_pron_sust,
                "ratio_func_cont":           ratio_func_cont,
            }
        }},
    )
    return res.modified_count > 0


# ── Consultas de utilidad ─────────────────────────────────────────────────────

def listar_artistas(collection=None) -> list[str]:
    """Retorna la lista de artistas únicos almacenados."""
    col = collection or _get_default_collection()
    return col.distinct("Artist")


def canciones_sin_metricas(collection=None) -> list[dict]:
    """Retorna documentos que aún no tienen métricas calculadas."""
    col = collection or _get_default_collection()
    return list(col.find({"metricas": None}, {"Song": 1, "Artist": 1, "Lyrics": 1}))


def canciones_por_artista(artista: str, collection=None) -> list[dict]:
    """Retorna todas las canciones de un artista."""
    col = collection or _get_default_collection()
    return list(col.find({"Artist": artista}))
