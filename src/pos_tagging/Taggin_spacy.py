import ast
import spacy
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(".."))
from src.data.mongo_storage import _get_default_collection, guardar_pos_tags


def apply_pos_tagging_spacy(df):
    nlp = spacy.load("en_core_web_sm")
    df = df.copy()

    # Convertir de string a lista si viene del CSV
    if isinstance(df['tokens'].iloc[0], str):
        df['tokens'] = df['tokens'].apply(ast.literal_eval)

    def tag_tokens(tokens):
        doc = nlp(" ".join(tokens))
        return [{"token": t.text, "pos": t.pos_, "tag": t.tag_, "lemma": t.lemma_} for t in doc]

    df['pos_tags_spacy'] = df['tokens'].apply(tag_tokens)

    # Guardar en MongoDB fila por fila
    col = _get_default_collection()
    actualizados = 0

    for _, row in df.iterrows():
        spacy_tags = row['pos_tags_spacy']

        # Recuperar nltk_tags existentes para no pisarlos
        doc = col.find_one({"_id": row["_id"]}, {"pos_tags": 1})
        nltk_tags = []
        if doc and doc.get("pos_tags") and doc["pos_tags"].get("nltk"):
            nltk_tags = doc["pos_tags"]["nltk"]

        ok = guardar_pos_tags(
            song_id=row["_id"],
            nltk_tags=nltk_tags,
            spacy_tags=spacy_tags,
        )
        if ok:
            actualizados += 1

    print(f"pos_tags.spacy guardados en MongoDB: {actualizados}/{len(df)} canciones")
    return df