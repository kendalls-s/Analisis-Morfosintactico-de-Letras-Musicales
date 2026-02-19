# -*- coding: utf-8 -*-
# data_cache.py - Load and process all data ONCE at server start
# All pages import pre-computed variables from here

import ast
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np

from src.data import carga_limpios, carga_pos_nltk, carga_pos_spacy
from src.analysis import calcular_metricas_spacy, resumen_global

print("[cache] Loading data (only happens once)...")

# 1. Clean dataset (EDA)
df_clean = carga_limpios()
df_clean["Lyrics_length"] = df_clean["Lyrics"].apply(lambda x: len(str(x).split()))
df_clean["Decade"] = (df_clean["Song year"] // 10) * 10
print("[cache] df_clean ready")

# 2. NLTK POS
df_nltk = carga_pos_nltk()
df_nltk["pos_tags"] = df_nltk["pos_tags"].apply(ast.literal_eval)
nltk_tags = [tag for row in df_nltk["pos_tags"] for _, tag in row]
print("[cache] df_nltk ready")

# 3. spaCy POS
df_spacy = carga_pos_spacy()
df_spacy["pos_tags_spacy"] = df_spacy["pos_tags_spacy"].apply(ast.literal_eval)
spacy_upos = [upos for row in df_spacy["pos_tags_spacy"] for _, upos, _, _ in row]
spacy_fine = [fine for row in df_spacy["pos_tags_spacy"] for _, _, fine, _ in row]
print("[cache] df_spacy ready")

# 4. Morphological metrics (notebook 05_analisis_morfologico)
df_metricas = calcular_metricas_spacy(df_spacy)
df_tot = resumen_global(df_metricas)
print("[cache] df_metricas ready")

# 5. Temporal features (notebook 06_evolucion_temporal)
def _ttr(pos_list):
    tokens = [t[0].lower() for t in pos_list]
    return len(set(tokens)) / len(tokens) if tokens else 0

def _density(pos_list, tag):
    total = len(pos_list)
    return sum(1 for t in pos_list if t[1] == tag) / total if total > 0 else 0

df_temporal = df_spacy[["Song", "Artist", "Genre", "Song year"]].copy()
df_temporal["Song year"]      = df_temporal["Song year"].astype(int)
df_temporal["decade"]         = (df_temporal["Song year"] // 10) * 10
df_temporal["song_length"]    = df_spacy["pos_tags_spacy"].apply(len)
df_temporal["ttr"]            = df_spacy["pos_tags_spacy"].apply(_ttr)
df_temporal["noun_density"]   = df_spacy["pos_tags_spacy"].apply(lambda x: _density(x, "NOUN"))
df_temporal["verb_density"]   = df_spacy["pos_tags_spacy"].apply(lambda x: _density(x, "VERB"))
df_temporal["noun_verb_ratio"]= df_temporal["noun_density"] / (df_temporal["verb_density"] + 1e-9)

yearly = df_temporal.groupby("Song year")[
    ["song_length", "ttr", "noun_density", "verb_density", "noun_verb_ratio"]
].mean()

decade_agg = df_temporal.groupby("decade")[
    ["song_length", "ttr", "noun_density", "verb_density"]
].mean().reset_index()
print("[cache] temporal aggregations ready")

# 6. Genre comparison features (notebook 05_comparacion_generos)
# Uses df_metricas columns: total_tokens, n_verbos, n_sustantivos, densidad_lexica, ttr
df_genero = df_metricas.copy()
for col in ["n_verbos", "n_sustantivos", "n_adjetivos", "n_adverbios", "n_pronombres"]:
    if col in df_genero.columns:
        df_genero[col + "_per1k"] = df_genero[col] / df_genero["total_tokens"].replace(0, 1) * 1000
ttr_col = "ttr" if "ttr" in df_genero.columns else "densidad_lexica"
print("[cache] df_genero ready")

print("[cache] All data loaded. Dashboard will respond instantly.")
