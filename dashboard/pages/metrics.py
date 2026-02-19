# -*- coding: utf-8 -*-
# Metrics page - combines notebooks 04 (comparative metrics) + 05 (resumen_global)
# Shows: KPI cards from notebook 04 print(), df_tot table, distributions
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_cache import nltk_tags, spacy_upos, spacy_fine, df_spacy, df_metricas, df_tot

dash.register_page(__name__, path="/metrics", name="Metricas", order=6)

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

# KPI values (notebook 04: print statements)
_uniq_nltk  = len(set(nltk_tags))
_uniq_upos  = len(set(spacy_upos))
_total_nltk = len(nltk_tags)
_total_spcy = len(spacy_upos)
_n_songs    = len(df_spacy)

# df_tot table rows
_cats   = ["n_sustantivos","n_verbos","n_adjetivos","n_adverbios",
           "n_pronombres","n_propios","n_auxiliares","n_interjecciones","n_numerales"]
_labels = ["Sustantivos","Verbos","Adjetivos","Adverbios",
           "Pronombres","Nombres Propios","Auxiliares","Interjecciones","Numerales"]
_avail  = [(c,l) for c,l in zip(_cats,_labels) if c in df_tot.index]

_tbl_rows = []
for cat, lab in _avail:
    val = int(df_tot.loc[cat,"total_corpus"])
    ppc = df_tot.loc[cat,"promedio_por_cancion"]
    pct = val / _total_spcy * 100 if _total_spcy > 0 else 0
    _tbl_rows.append(html.Tr([
        html.Td(lab, style={"fontFamily":"Inter,sans-serif","fontSize":"0.78rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5"}),
        html.Td(f"{val:,}", style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.78rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right","fontWeight":"600","color":"#6A1B9A"}),
        html.Td(f"{ppc:.2f}", style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.78rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right"}),
        html.Td(f"{pct:.2f}%", style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.78rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right","color":"#8E24AA"}),
    ]))

# Bar chart from df_tot
_bar_df = pd.DataFrame({"Categoria":[l for _,l in _avail],
    "Total": [int(df_tot.loc[c,"total_corpus"]) for c,_ in _avail]})
fig_global = fig_base(px.bar(_bar_df, x="Total", y="Categoria", orientation="h",
    color="Total", color_continuous_scale="Purples",
    labels={"Total":"Tokens totales","Categoria":""},
    text="Total"))
fig_global.update_traces(texttemplate="%{text:,}", textposition="outside")
fig_global.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))

# Distributions
fig_lex = fig_base(px.histogram(df_metricas, x="densidad_lexica", nbins=50,
    color_discrete_sequence=["#880E4F"],
    labels={"densidad_lexica":"Densidad Lexica","count":"Frecuencia"}))
fig_lex.update_layout(bargap=0.03)

fig_tok = fig_base(px.histogram(df_metricas, x="total_tokens", nbins=50,
    color_discrete_sequence=["#7C4DFF"],
    labels={"total_tokens":"Tokens por cancion","count":"Frecuencia"}))
fig_tok.update_layout(bargap=0.03)

_sample = df_metricas.sample(min(1500,len(df_metricas)), random_state=42)
fig_scatter = fig_base(px.scatter(_sample, x="total_tokens", y="densidad_lexica",
    color="Genre", color_discrete_sequence=PAL, opacity=0.55,
    labels={"total_tokens":"Tokens","densidad_lexica":"Densidad Lexica","Genre":"Genero"}))
fig_scatter.update_traces(marker_size=4)
fig_scatter.update_layout(legend=dict(font=dict(size=9)))

layout = html.Div([
    html.H2("Metricas Globales"),
    html.P("Resumen cuantitativo del corpus - notebooks 04 (metricas comparativas) y 05 (resumen_global)",
           className="page-sub"),

    # Notebook 04 print() metrics
    dbc.Row([
        dbc.Col(html.Div([html.Div(f"{_n_songs:,}",    className="metric-value"), html.Div("Canciones totales",       className="metric-label")], className="metric-card"), xs=6, md=2),
        dbc.Col(html.Div([html.Div(f"{_total_spcy:,}", className="metric-value", style={"fontSize":"1.3rem"}), html.Div("Total tokens spaCy", className="metric-label")], className="metric-card"), xs=6, md=2),
        dbc.Col(html.Div([html.Div(f"{_total_nltk:,}", className="metric-value", style={"fontSize":"1.3rem"}), html.Div("Total tokens NLTK",  className="metric-label")], className="metric-card"), xs=6, md=2),
        dbc.Col(html.Div([html.Div(str(_uniq_upos),    className="metric-value"), html.Div("Tags unicos spaCy Universal", className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(str(_uniq_nltk),    className="metric-value"), html.Div("Tags unicos NLTK Penn",       className="metric-label")], className="metric-card"), xs=6, md=3),
    ], className="g-2", style={"marginBottom":"1.25rem"}),

    dbc.Row([
        dbc.Col(card("Total por Categoria Gramatical (spaCy - df_tot)",
            dcc.Graph(figure=fig_global, config={"displayModeBar":False}, style={"height":"340px"})), md=7),
        dbc.Col([
            html.Div("resumen_global(df_metricas) - total_corpus | promedio | % corpus", className="section-title"),
            html.Div(html.Table([
                html.Thead(html.Tr([
                    html.Th("Categoria",      style={"fontFamily":"Inter","fontSize":"0.72rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A"}),
                    html.Th("Total",          style={"fontFamily":"Inter","fontSize":"0.72rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A","textAlign":"right"}),
                    html.Th("Prom/cancion",   style={"fontFamily":"Inter","fontSize":"0.72rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A","textAlign":"right"}),
                    html.Th("% corpus",       style={"fontFamily":"Inter","fontSize":"0.72rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A","textAlign":"right"}),
                ])),
                html.Tbody(_tbl_rows),
            ], style={"width":"100%","borderCollapse":"collapse"})),
        ], className="card-panel", md=5),
    ], className="g-0"),

    dbc.Row([
        dbc.Col(card("Distribucion Densidad Lexica por cancion", dcc.Graph(figure=fig_lex, config={"displayModeBar":False}, style={"height":"250px"})), md=6),
        dbc.Col(card("Distribucion Tokens por cancion",          dcc.Graph(figure=fig_tok, config={"displayModeBar":False}, style={"height":"250px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Tokens vs Densidad Lexica por Genero (muestra aleatoria 1500)",
            dcc.Graph(figure=fig_scatter, config={"displayModeBar":False}, style={"height":"300px"})), md=12),
    ], className="g-0"),
])
