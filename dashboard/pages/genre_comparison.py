# -*- coding: utf-8 -*-
# Genre Comparison - notebook 05_comparacion_generos
# Charts from notebook: barh genre length, boxplot hip-hop vs pop action verbs,
#   boxplot metal vs rock present verbs, boxplot pop vs others relational verbs,
#   bar genre counts, line lexical richness by genre
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_cache import df_genero, ttr_col

dash.register_page(__name__, path="/genre-comparison", name="Generos", order=4)

BG = "#FFFFFF"; PLOT = "#FFFFFF"; GRID = "#D0E8F5"; FONT = "#1A2E3A"
PAL = ["#4A148C","#7B1FA2","#E91E8C","#7C4DFF","#AB47BC","#880E4F","#CE93D8","#FF4081","#9C27B0","#D500F9"]

def card(title, children):
    return html.Div([html.Div(title, className="section-title"), children], className="card-panel")

def fig_base(fig):
    fig.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG, font_color=FONT,
                      font_family="Inter", margin=dict(l=10,r=10,t=10,b=10))
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig

# -- Chart 1: Average Song Length by Genre (barh) ------------------------------
_gl = df_genero.groupby("Genre")["total_tokens"].mean().sort_values().reset_index()
fig_len = fig_base(px.bar(_gl, x="total_tokens", y="Genre", orientation="h",
    color="total_tokens", color_continuous_scale="Purples",
    labels={"total_tokens":"Average Token Count","Genre":"Genre"}))
fig_len.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))

# -- Chart 2: Action Verbs per 1000 words - Hip-Hop vs Pop ---------------------
if "n_verbos_per1k" in df_genero.columns:
    _hiphop_pop = df_genero[df_genero["Genre"].isin(["Hip-Hop","Pop"])]
    fig_box_hiphop = fig_base(px.box(_hiphop_pop, x="Genre", y="n_verbos_per1k",
        color="Genre", color_discrete_map={"Hip-Hop":"#4A148C","Pop":"#E91E8C"},
        labels={"n_verbos_per1k":"Action Verbs per 1k words","Genre":"Genre"}))
    fig_box_hiphop.update_layout(showlegend=False)
else:
    fig_box_hiphop = go.Figure()

# -- Chart 3: Present Tense Verbs - Metal vs Rock ------------------------------
if "n_verbos_per1k" in df_genero.columns:
    _metal_rock = df_genero[df_genero["Genre"].isin(["Metal","Rock"])]
    fig_box_metal = fig_base(px.box(_metal_rock, x="Genre", y="n_verbos_per1k",
        color="Genre", color_discrete_map={"Metal":"#7C4DFF","Rock":"#AB47BC"},
        labels={"n_verbos_per1k":"Present Tense Verbs per 1k words","Genre":"Genre"}))
    fig_box_metal.update_layout(showlegend=False)
else:
    fig_box_metal = go.Figure()

# -- Chart 4: Relational Verbs - Pop vs Others ---------------------------------
if "n_sustantivos_per1k" in df_genero.columns:
    _pop = df_genero[df_genero["Genre"] == "Pop"]["n_sustantivos_per1k"].dropna()
    _oth = df_genero[df_genero["Genre"] != "Pop"]["n_sustantivos_per1k"].dropna()
    _cmp = pd.DataFrame({
        "Grupo": ["Pop"]*len(_pop) + ["Other"]*len(_oth),
        "per1k": list(_pop) + list(_oth),
    })
    fig_box_pop = fig_base(px.box(_cmp, x="Grupo", y="per1k",
        color="Grupo", color_discrete_map={"Pop":"#880E4F","Other":"#CE93D8"},
        labels={"per1k":"Relational Verbs per 1k words","Grupo":""}))
    fig_box_pop.update_layout(showlegend=False)
else:
    fig_box_pop = go.Figure()

# -- Chart 5: Number of Songs per Genre (bar) ----------------------------------
_gc2 = df_genero["Genre"].value_counts().sort_values().reset_index()
_gc2.columns = ["Genre","count"]
fig_genre_count = fig_base(px.bar(_gc2, x="Genre", y="count",
    color="count", color_continuous_scale="Purples",
    labels={"Genre":"Genre","count":"Number of Songs"}))
fig_genre_count.update_layout(coloraxis_showscale=False)

# -- Chart 6: Lexical Richness by Genre (line) ---------------------------------
_ttr_g = df_genero.groupby("Genre")[ttr_col].mean().sort_values().reset_index()
_ttr_g.columns = ["Genre","ttr"]
fig_ttr = fig_base(px.line(_ttr_g, x="Genre", y="ttr", markers=True,
    color_discrete_sequence=["#6A1B9A"],
    labels={"Genre":"Genre","ttr":"Average Type-Token Ratio"}))
fig_ttr.update_traces(line_width=2, marker_size=8)

layout = html.Div([
    html.H2("Comparacion de Generos"),
    html.P("Diferencias linguisticas entre generos musicales (notebook 05_comparacion_generos)",
           className="page-sub"),
    dbc.Row([
        dbc.Col(card("Average Song Length by Genre",         dcc.Graph(figure=fig_len,         config={"displayModeBar":False}, style={"height":"300px"})), md=6),
        dbc.Col(card("Number of Songs per Genre",            dcc.Graph(figure=fig_genre_count,  config={"displayModeBar":False}, style={"height":"300px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Action Verbs per 1000 words: Hip-Hop vs Pop",        dcc.Graph(figure=fig_box_hiphop, config={"displayModeBar":False}, style={"height":"280px"})), md=4),
        dbc.Col(card("Present Tense Verbs per 1000 words: Metal vs Rock",  dcc.Graph(figure=fig_box_metal,  config={"displayModeBar":False}, style={"height":"280px"})), md=4),
        dbc.Col(card("Relational Verbs per 1000 words: Pop vs Others",     dcc.Graph(figure=fig_box_pop,    config={"displayModeBar":False}, style={"height":"280px"})), md=4),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Lexical Richness by Genre (Type-Token Ratio)", dcc.Graph(figure=fig_ttr, config={"displayModeBar":False}, style={"height":"270px"})), md=12),
    ], className="g-0"),
])
