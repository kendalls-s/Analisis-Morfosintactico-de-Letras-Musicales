# -*- coding: utf-8 -*-
# Morfological Analysis - notebook 05_analisis_morfologico
# Charts: bar + pie categorias, bar densidad lexica por genero, boxplot total_tokens
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_cache import df_metricas, df_tot

dash.register_page(__name__, path="/morphological", name="Morfologico", order=3)

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

# -- Chart 1+2: Distribucion Global de Categorias Gramaticales -----------------
# (notebook cell: cats/labels/valores = df_tot.loc[cats,'total_corpus'])
_cats   = ["n_sustantivos","n_verbos","n_adjetivos","n_adverbios",
           "n_pronombres","n_propios","n_auxiliares","n_interjecciones","n_numerales"]
_labels = ["Sustantivos","Verbos","Adjetivos","Adverbios",
           "Pronombres","Propios","Auxiliares","Interjecciones","Numerales"]
_avail  = [(c,l) for c,l in zip(_cats,_labels) if c in df_tot.index]
_acat, _alab = zip(*_avail) if _avail else ([],[])
_vals   = df_tot.loc[list(_acat), "total_corpus"]
_cat_df = pd.DataFrame({"Categoria": list(_alab), "Total": _vals.values})

fig_cats = fig_base(px.bar(_cat_df, x="Total", y="Categoria", orientation="h",
    color="Total", color_continuous_scale="Purples",
    labels={"Total":"Cantidad de tokens","Categoria":""}))
fig_cats.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))

fig_pie = fig_base(px.pie(_cat_df, names="Categoria", values="Total",
    color_discrete_sequence=PAL, hole=0.4))
fig_pie.update_layout(legend=dict(font=dict(size=9)))

# -- Chart 3: Densidad Lexica Media por Genero ---------------------------------
# (notebook cell: medias = df_metricas.groupby('Genre')['densidad_lexica'].mean())
_medias = df_metricas.groupby("Genre")["densidad_lexica"].mean().sort_values(ascending=False).reset_index()
fig_lex = fig_base(px.bar(_medias, x="Genre", y="densidad_lexica",
    color="densidad_lexica", color_continuous_scale="Purples",
    labels={"Genre":"Genero","densidad_lexica":"Densidad Lexica Media"},
    text="densidad_lexica"))
fig_lex.update_traces(texttemplate="%{text:.3f}", textposition="outside")
fig_lex.update_layout(coloraxis_showscale=False)

# -- Chart 4+5: Distribucion total_tokens por Genero ---------------------------
# (notebook cell: boxplot + histogram overlaid)
_order = df_metricas.groupby("Genre")["total_tokens"].median().sort_values(ascending=False).index.tolist()
fig_box = fig_base(px.box(df_metricas, x="Genre", y="total_tokens",
    color="Genre", color_discrete_sequence=PAL,
    category_orders={"Genre": _order},
    labels={"Genre":"Genero","total_tokens":"Total de Tokens"}))
fig_box.update_layout(showlegend=False)

fig_hist_genre = fig_base(px.histogram(df_metricas, x="total_tokens",
    color="Genre", color_discrete_sequence=PAL,
    barmode="overlay", opacity=0.5,
    labels={"total_tokens":"Total de Tokens","count":"Frecuencia"}))
fig_hist_genre.update_layout(legend=dict(font=dict(size=9)))

# -- Table: df_tot resumen global (notebook: print(df_tot)) --------------------
_tot_rows = []
for idx in df_tot.index:
    if idx in ("densidad_lexica","ttr","ratio_sust_verb","ratio_adj_sust","ratio_adv_verb","ratio_pron_sust","ratio_func_cont"):
        _tot_rows.append(html.Tr([
            html.Td(idx, style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.75rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","color":"#8E24AA"}),
            html.Td(f"{df_tot.loc[idx,'total_corpus']:.4f}", style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.75rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right"}),
            html.Td(f"{df_tot.loc[idx,'promedio_por_cancion']:.4f}", style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.75rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right","color":"#6A1B9A"}),
        ]))
    else:
        _tot_rows.append(html.Tr([
            html.Td(idx, style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.75rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5"}),
            html.Td(f"{int(df_tot.loc[idx,'total_corpus']):,}", style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.75rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right","fontWeight":"600","color":"#6A1B9A"}),
            html.Td(f"{df_tot.loc[idx,'promedio_por_cancion']:.2f}", style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.75rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right"}),
        ]))

_best = _medias.iloc[0]["Genre"]
_worst= _medias.iloc[-1]["Genre"]

layout = html.Div([
    html.H2("Analisis Morfologico"),
    html.P("Metricas morfologicas calculadas con spaCy (notebook 05_analisis_morfologico)",
           className="page-sub"),
    dbc.Row([
        dbc.Col(html.Div([html.Div(f"{int(df_tot.loc['total_tokens','total_corpus']):,}", className="metric-value", style={"fontSize":"1.5rem"}), html.Div("Tokens totales corpus", className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(str(round(df_metricas["densidad_lexica"].mean(),3)), className="metric-value"), html.Div("Densidad lexica media", className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(_best, className="metric-value", style={"fontSize":"1.1rem"}), html.Div("Mayor densidad lexica", className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(_worst,className="metric-value", style={"fontSize":"1.1rem"}), html.Div("Menor densidad lexica", className="metric-label")], className="metric-card"), xs=6, md=3),
    ], className="g-2", style={"marginBottom":"1.25rem"}),

    dbc.Row([
        dbc.Col(card("Total por Categoria Gramatical en el Corpus", dcc.Graph(figure=fig_cats, config={"displayModeBar":False}, style={"height":"300px"})), md=6),
        dbc.Col(card("Distribucion porcentual de Categorias", dcc.Graph(figure=fig_pie, config={"displayModeBar":False}, style={"height":"300px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Densidad Lexica Media por Genero", dcc.Graph(figure=fig_lex, config={"displayModeBar":False}, style={"height":"280px"})), md=12),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Longitud de Canciones (tokens) por Genero - Boxplot", dcc.Graph(figure=fig_box,       config={"displayModeBar":False}, style={"height":"280px"})), md=6),
        dbc.Col(card("Distribucion de Longitud por Genero - Histograma",    dcc.Graph(figure=fig_hist_genre, config={"displayModeBar":False}, style={"height":"280px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            html.Div("Resumen Global del Corpus - df_tot (total_corpus | promedio_por_cancion)", className="section-title"),
            html.Div(html.Table([
                html.Thead(html.Tr([
                    html.Th("Metrica",              style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A"}),
                    html.Th("Total Corpus",         style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A","textAlign":"right"}),
                    html.Th("Promedio por Cancion", style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A","textAlign":"right"}),
                ])),
                html.Tbody(_tot_rows),
            ], style={"width":"100%","borderCollapse":"collapse"})),
        ], className="card-panel", md=12),
    ], className="g-0"),
])
