import ast #Convierte un string que parece una lista en una lista real de Python.
import spacy
from pathlib import Path

def apply_pos_tagging_spacy(df):
    nlp = spacy.load("en_core_web_sm")
    df = df.copy()

    # Convertir de string a lista si viene del CSV
    if isinstance(df['tokens'].iloc[0], str):
        df['tokens'] = df['tokens'].apply(ast.literal_eval)

    def tag_tokens(tokens):
        doc = nlp(" ".join(tokens))
        return [(token.text, token.pos_, token.tag_, token.lemma_) for token in doc]

    df['pos_tags_spacy'] = df['tokens'].apply(tag_tokens)

    # Construir ruta destino
    project_root = Path.cwd().parent
    output_path = project_root / "data" / "processed" / "lyrics_pos_tagged_spacy.csv"

    # Guardar archivo
    df.to_csv(output_path, index=False, encoding="utf-8")
    return df
