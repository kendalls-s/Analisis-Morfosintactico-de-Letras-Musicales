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
