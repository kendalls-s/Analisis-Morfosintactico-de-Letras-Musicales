def comparar_nltk_spacy_csv(df_nltk, df_spacy, indice=0):
    row_nltk  = df_nltk.iloc[indice]
    row_spacy = df_spacy.iloc[indice]

    nltk_tags  = row_nltk['pos_tags']
    spacy_tags = row_spacy['pos_tags_spacy']

    # ── Alinear por token ─────────────────────────────────────
    nltk_dict  = {token: tag for token, tag in nltk_tags}
    spacy_dict = {token: (upos, fine, lemma) for token, upos, fine, lemma in spacy_tags}

    tokens_comunes = [t for t in nltk_dict if t in spacy_dict]

    print("=" * 85)
    print("COMPARACIÓN: NLTK vs spaCy")
    print("=" * 85)
    print(f"Canción : {row_nltk['Song']}")
    print(f"Artista : {row_nltk['Artist']}")
    print(f"Género  : {row_nltk['Genre']}\n")

    print(f"{'Token':<20} {'NLTK (Penn)':<15} {'spaCy Universal':<18} {'spaCy Fine':<15} {'Lemma'}")
    print("-" * 85)

    resultados = []

    for token in tokens_comunes:
        tag_nltk = nltk_dict[token]
        upos, fine, lemma = spacy_dict[token]

        print(f"{token:<20} {tag_nltk:<15} {upos:<18} {fine:<15} {lemma}")

        resultados.append({
            'Song':            row_nltk['Song'],
            'Artist':          row_nltk['Artist'],
            'Genre':           row_nltk['Genre'],
            'token':           token,
            'nltk_tag':        tag_nltk,
            'spacy_universal': upos,
            'spacy_fine':      fine,
            'lemma':           lemma
        })

    total = len(resultados)

    print(f"\nTokens comparados : {total}")
    print(f"Tokens solo NLTK  : {len(nltk_dict)  - total}")
    print(f"Tokens solo spaCy : {len(spacy_dict) - total}")