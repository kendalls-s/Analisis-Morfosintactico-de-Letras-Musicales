from collections import Counter
from pathlib import Path
import pandas as pd

def calcular_metricas_spacy(df_spacy):
    """
    Calcula métricas morfosintácticas por canción usando spaCy.
    """
    resultados = []

    for _, row in df_spacy.iterrows():
        tags = row['pos_tags_spacy']

        tokens = [t for t, _, _, _ in tags]
        lemas  = [l for _, _, _, l in tags]
        upos   = [p for _, p, _, _ in tags]

        total = len(tokens)
        if total == 0:
            continue

        cnt = Counter(upos)

        n_sust  = cnt['NOUN']  + cnt['PROPN']
        n_verb  = cnt['VERB']  + cnt['AUX']
        n_adj   = cnt['ADJ']
        n_adv   = cnt['ADV']
        n_pron  = cnt['PRON']
        n_det   = cnt['DET']
        n_prep  = cnt['ADP']
        n_conj  = cnt['CCONJ'] + cnt['SCONJ']
        n_num   = cnt['NUM']
        n_intj  = cnt['INTJ']
        n_propn = cnt['PROPN']
        n_aux   = cnt['AUX']

        contenido    = n_sust + cnt['VERB'] + n_adj + n_adv
        densidad_lex = contenido / total
        ttr          = len(set(lemas)) / total

        ratio_sust_verb = n_sust / n_verb if n_verb > 0 else 0
        ratio_adj_sust  = n_adj  / n_sust if n_sust > 0 else 0
        ratio_adv_verb  = n_adv  / n_verb if n_verb > 0 else 0
        ratio_pron_sust = n_pron / n_sust if n_sust > 0 else 0
        ratio_func_cont = (n_det + n_prep + n_conj + n_pron) / contenido if contenido > 0 else 0

        resultados.append({
            'Song':             row['Song'],
            'Artist':           row['Artist'],
            'Genre':            row['Genre'],
            'Song_year':        row['Song year'],
            'total_tokens':     total,
            'vocab_unico':      len(set(lemas)),
            'n_sustantivos':    n_sust,
            'n_verbos':         n_verb,
            'n_adjetivos':      n_adj,
            'n_adverbios':      n_adv,
            'n_pronombres':     n_pron,
            'n_propios':        n_propn,
            'n_auxiliares':     n_aux,
            'n_interjecciones': n_intj,
            'n_numerales':      n_num,
            'densidad_lexica':  round(densidad_lex, 4),
            'ttr':              round(ttr, 4),
            'ratio_sust_verb':  round(ratio_sust_verb, 4),
            'ratio_adj_sust':   round(ratio_adj_sust,  4),
            'ratio_adv_verb':   round(ratio_adv_verb,  4),
            'ratio_pron_sust':  round(ratio_pron_sust, 4),
            'ratio_func_cont':  round(ratio_func_cont, 4),
        })

    # ── convertir a DataFrame y guardar ──────────────────────
    df_resultado = pd.DataFrame(resultados)

    project_root = Path.cwd().parent
    output_path  = project_root / "data" / "results" / "metricas_spacy.csv"
    df_resultado.to_csv(output_path, index=False, encoding="utf-8")
    print(f"✔ metricas_spacy.csv guardado ({len(df_resultado)} canciones)")

    return df_resultado


def resumen_global(df_metricas):
    """Imprime y guarda métricas globales descriptivas."""
    print("=== MÉTRICAS GLOBALES (estadísticas por canción) ===")
    df_global = df_metricas.describe().round(3)

    # ── Totales generales del corpus ──────────────────────────
    cols_conteo = ['total_tokens', 'vocab_unico', 'n_sustantivos', 'n_verbos',
                   'n_adjetivos', 'n_adverbios', 'n_pronombres', 'n_propios',
                   'n_auxiliares', 'n_interjecciones', 'n_numerales']

    df_totales = df_metricas[cols_conteo].sum().rename('total_corpus').to_frame()
    df_totales['promedio_por_cancion'] = df_metricas[cols_conteo].mean().round(2)

    print("\n=== TOTALES DEL CORPUS ===")
    print(df_totales.to_string())

    project_root = Path.cwd().parent

    df_global.to_csv(project_root / "data" / "results" / "metricas_globales.csv",
                     index=True, encoding="utf-8")
    df_totales.to_csv(project_root / "data" / "results" / "totales_corpus.csv",
                      index=True, encoding="utf-8")

    return df_totales