from nltk.tag import pos_tag
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(".."))
from src.data.mongo_storage import _get_default_collection, guardar_pos_tags


def apply_pos_tagging_nltk(df):
    """
    Aplica POS tagging con NLTK sobre la columna 'tokens' del DataFrame
    y guarda el resultado en MongoDB (campo pos_tags.nltk).
    """
    df['pos_tags'] = df['tokens'].apply(lambda tokens: pos_tag(tokens))

    # Guardar en MongoDB fila por fila
    col = _get_default_collection()
    actualizados = 0

    for _, row in df.iterrows():
        # pos_tag devuelve lista de tuplas → convertir a lista de dicts para Mongo
        nltk_tags = [{"token": t, "tag": tag} for t, tag in row['pos_tags']]

        # Recuperar spacy_tags existentes en Mongo para no pisarlos
        doc = col.find_one({"_id": row["_id"]}, {"pos_tags": 1})
        spacy_tags = []
        if doc and doc.get("pos_tags") and doc["pos_tags"].get("spacy"):
            spacy_tags = doc["pos_tags"]["spacy"]

        ok = guardar_pos_tags(
            song_id=row["_id"],
            nltk_tags=nltk_tags,
            spacy_tags=spacy_tags,
        )
        if ok:
            actualizados += 1

    print(f"pos_tags.nltk guardados en MongoDB: {actualizados}/{len(df)} canciones")
    return df