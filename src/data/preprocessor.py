from pathlib import Path
from nltk.tokenize import word_tokenize

def token_nltk(df):
    """
    Tokeniza la columna Lyrics y guarda el resultado en data/processed/
    """
    # Tokenización
    df['tokens'] = df['Lyrics'].apply(lambda x: word_tokenize(x))

    # Construir ruta destino
    project_root = Path.cwd().parent
    output_path = project_root / "data" / "processed" / "lyrics_tokenized_nltk.csv"

    # Guardar archivo
    df.to_csv(output_path, index=False, encoding="utf-8")
    return df


import spacy
import pandas as pd
from pathlib import Path

# Variable global para el modelo
_nlp = None


def _cargar_spacy(modelo="en_core_web_sm"):
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load(modelo)
        except OSError:
            print(f"Modelo {modelo} no encontrado. Descargando...")
            spacy.cli.download(modelo)
            _nlp = spacy.load(modelo)
    return _nlp


def token_spacy(df):
    """
    Tokeniza la columna 'Lyrics' usando spaCy y guarda en data/processed/
    """
    nlp = _cargar_spacy()
    df['tokens'] = df['Lyrics'].apply(lambda x: [token.text for token in nlp(str(x))])

    # Ruta de salida
    project_root = Path(__file__).resolve().parents[2]
    output_path = project_root / "data" / "processed" / "lyrics_tokenized_spacy.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    return df