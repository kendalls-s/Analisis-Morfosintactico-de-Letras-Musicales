from collections import Counter
from pathlib import Path
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(".."))
from src.data.mongo_storage import _get_default_collection, guardar_metricas


def calcular_metricas_spacy(df_spacy):
    """
    Calcula métricas morfosintácticas por canción usando los pos_tags
    de spaCy y guarda el resultado en MongoDB.
    """
    col = _get_default_collection()
    resultados = []
    actualizados = 0

    for _, row in df_spacy.iterrows():
        tags = row['pos_tags_spacy']

        # Soporta tanto lista de tuplas (CSV) como lista de dicts (Mongo)
        if tags and isinstance(tags[0], dict):
            tokens = [t['token'] for t in tags]
            lemas  = [t['lemma']  for t in tags]
            upos   = [t['pos']    for t in tags]
        else:
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

        # Guardar en MongoDB
        ok = guardar_metricas(
            song_id=row["_id"],
            num_palabras=total,
            vocab_unico=len(set(lemas)),
            n_sustantivos=n_sust,
            n_verbos=n_verb,
            n_adjetivos=n_adj,
            n_adverbios=n_adv,
            n_pronombres=n_pron,
            n_propios=n_propn,
            n_auxiliares=n_aux,
            n_interjecciones=n_intj,
            n_numerales=n_num,
            densidad_lexica=round(densidad_lex, 4),
            ttr=round(ttr, 4),
            ratio_sustantivos_verbos=round(ratio_sust_verb, 4),
            ratio_adj_sust=round(ratio_adj_sust, 4),
            ratio_adv_verb=round(ratio_adv_verb, 4),
            ratio_pron_sust=round(ratio_pron_sust, 4),
            ratio_func_cont=round(ratio_func_cont, 4),
        )
        if ok:
            actualizados += 1

        resultados.append({
            '_id':              row['_id'],
            'Song':             row['Song'],
            'Artist':           row['Artist'],
            'Genre':            row['Genre'],
            'Song year':        row['Song year'],
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

    df_resultado = pd.DataFrame(resultados)
    print(f"✓ métricas guardadas en MongoDB: {actualizados}/{len(df_spacy)} canciones")
    return df_resultado


def resumen_global(df_metricas):
    """Imprime y retorna métricas globales descriptivas."""
    print("=== MÉTRICAS GLOBALES (estadísticas por canción) ===")

    cols_conteo = ['total_tokens', 'vocab_unico', 'n_sustantivos', 'n_verbos',
                   'n_adjetivos', 'n_adverbios', 'n_pronombres', 'n_propios',
                   'n_auxiliares', 'n_interjecciones', 'n_numerales']

    df_totales = df_metricas[cols_conteo].sum().rename('total_corpus').to_frame()
    df_totales['promedio_por_cancion'] = df_metricas[cols_conteo].mean().round(2)

    print("\n=== TOTALES DEL CORPUS ===")
    print(df_totales.to_string())

    return df_totales