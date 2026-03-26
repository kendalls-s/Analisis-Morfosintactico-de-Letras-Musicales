from pymongo import MongoClient, UpdateOne
from bson import ObjectId
from datetime import datetime, timezone
import pandas as pd

_DEFAULT_URI = "mongodb://localhost:27017"
_DEFAULT_DB  = "musica"
_DEFAULT_COL = "canciones"

def get_collection(uri: str = _DEFAULT_URI, db: str = _DEFAULT_DB, col: str = _DEFAULT_COL):
    client = MongoClient(uri)
    return client[db][col]

_default_collection = None

def _get_default_collection():
    global _default_collection
    if _default_collection is None:
        _default_collection = get_collection()
    return _default_collection


def _to_object_id(value):
    try:
        return ObjectId(value)
    except Exception:
        return ObjectId()


def insertar_canciones_csv(df: pd.DataFrame, collection=None) -> dict:
    col = collection or _get_default_collection()
    operaciones = []

    for _, row in df.iterrows():
        doc = {
            "_id":             _to_object_id(row.get("_id")),
            "Song":            row.get("Song"),
            "Artist":          row.get("Artist"),
            "Genre":           row.get("Genre"),
            "Song year":       int(row["Song year"]),
            "Lyrics":          row.get("Lyrics"),
            "Language":        row.get("Language"),
            "Source":          row.get("Source"),
            "Url":             row.get("Url"),
            "collection_date": row.get("collection_date"),
            "pos_tags":        None,
            "embeddings":      None,
            "metricas":        None,
        }

        operaciones.append(
            UpdateOne(
                {"_id": doc["_id"]},
                {"$setOnInsert": doc},
                upsert=True
            )
        )

    if not operaciones:
        return {"insertados": 0, "actualizados": 0}

    resultado = col.bulk_write(operaciones, ordered=False)
    return {
        "insertados":   resultado.upserted_count,
        "actualizados": resultado.matched_count,
    }


def guardar_pos_tags(song_id, nltk_tags: list, spacy_tags: list, collection=None) -> bool:
    col = collection or _get_default_collection()
    resultado = col.update_one(
        {"_id": _to_object_id(song_id)},
        {"$set": {
            "pos_tags": {
                "nltk":  nltk_tags,
                "spacy": spacy_tags,
            }
        }}
    )
    return resultado.modified_count > 0


def guardar_embeddings(song_id, word2vec_avg: list, beto_cls: list, collection=None) -> bool:
    col = collection or _get_default_collection()
    resultado = col.update_one(
        {"_id": _to_object_id(song_id)},
        {"$set": {
            "embeddings": {
                "word2vec_avg": word2vec_avg,
                "beto_cls":    beto_cls,
            }
        }}
    )
    return resultado.modified_count > 0


def guardar_metricas(song_id,
                     num_palabras: int,
                     vocab_unico: int,
                     n_sustantivos: int,
                     n_verbos: int,
                     n_adjetivos: int,
                     n_adverbios: int,
                     n_pronombres: int,
                     n_propios: int,
                     n_auxiliares: int,
                     n_interjecciones: int,
                     n_numerales: int,
                     densidad_lexica: float,
                     ttr: float,
                     ratio_sustantivos_verbos: float,
                     ratio_adj_sust: float,
                     ratio_adv_verb: float,
                     ratio_pron_sust: float,
                     ratio_func_cont: float,
                     collection=None) -> bool:
    col = collection or _get_default_collection()
    resultado = col.update_one(
        {"_id": _to_object_id(song_id)},
        {"$set": {
            "metricas": {
                "num_palabras":             num_palabras,
                "vocab_unico":              vocab_unico,
                "n_sustantivos":            n_sustantivos,
                "n_verbos":                 n_verbos,
                "n_adjetivos":              n_adjetivos,
                "n_adverbios":              n_adverbios,
                "n_pronombres":             n_pronombres,
                "n_propios":                n_propios,
                "n_auxiliares":             n_auxiliares,
                "n_interjecciones":         n_interjecciones,
                "n_numerales":              n_numerales,
                "densidad_lexica":          densidad_lexica,
                "ttr":                      ttr,
                "ratio_sustantivos_verbos": ratio_sustantivos_verbos,
                "ratio_adj_sust":           ratio_adj_sust,
                "ratio_adv_verb":           ratio_adv_verb,
                "ratio_pron_sust":          ratio_pron_sust,
                "ratio_func_cont":          ratio_func_cont,
            }
        }}
    )
    return resultado.modified_count > 0


if __name__ == "__main__":
    df = pd.read_csv("data/processed/lyrics_clean.csv")

    resumen = insertar_canciones_csv(df)
    print("Inserción CSV:", resumen)

    ejemplo_id = df.iloc[0]["_id"]

    guardar_pos_tags(
        song_id=ejemplo_id,
        nltk_tags=[("Most", "JJS"), ("folks", "NNS")],
        spacy_tags=[{"text": "Most", "pos": "ADJ"}, {"text": "folks", "pos": "NOUN"}],
    )

    guardar_embeddings(
        song_id=ejemplo_id,
        word2vec_avg=[0.12, -0.34, 0.56],
        beto_cls=[0.98, 0.01, -0.45],
    )

    guardar_metricas(
        song_id=ejemplo_id,
        num_palabras=250,
        densidad_lexica=0.65,
        ratio_sustantivos_verbos=1.2,
    )

    print("Todo guardado correctamente.")