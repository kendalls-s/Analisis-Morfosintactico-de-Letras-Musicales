import spacy


def _cargar_spacy_pos(modelo="en_core_web_sm"):
    global _nlp_pos
    if _nlp_pos is None:
        try:
            _nlp_pos = spacy.load(modelo)
        except OSError:
            print(f"Modelo {modelo} no encontrado. Descargando...")
            spacy.cli.download(modelo)
            _nlp_pos = spacy.load(modelo)
    return _nlp_pos


def apply_pos_tagging_spacy(df, text_col='lyrics_clean'):
    """
    Aplica POS tagging con spaCy al texto de la columna 'text_col'.
    Añade una columna 'pos_tags_spacy' con listas de tuplas (token, pos_tag).
    Guarda el resultado en data/processed/lyrics_pos_tagged_spacy.csv
    """
    nlp = _cargar_spacy_pos()

    # Procesar todos los textos en lote para mayor eficiencia
    textos = df[text_col].astype(str).tolist()
    docs = nlp.pipe(textos, batch_size=50)

    # Extraer tokens y POS tags
    df['pos_tags_spacy'] = [
        [(token.text, token.pos_) for token in doc]
        for doc in docs
    ]

    # Guardar archivo
    project_root = Path(__file__).resolve().parents[2]  # ajusta según tu estructura
    output_path = project_root / "data" / "processed" / "lyrics_pos_tagged_spacy.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    return df