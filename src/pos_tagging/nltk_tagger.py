from nltk.tag import pos_tag
from pathlib import Path

def apply_pos_tagging_nltk(df):
    df['pos_tags'] = df['tokens'].apply(lambda tokens: pos_tag(tokens))

    # Construir ruta destino
    project_root = Path.cwd().parent
    output_path = project_root / "data" / "processed" / "lyrics_pos_tagged_nltk.csv"

    # Guardar archivo
    df.to_csv(output_path, index=False, encoding="utf-8")

    return df


import spacy
import pandas as pd
from pathlib import Path

# Cargar modelo una sola vez (similar a como hicimos con token_spacy)
_nlp_pos = None


