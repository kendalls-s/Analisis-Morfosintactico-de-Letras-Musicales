# -*- coding: utf-8 -*-
# POS Distributions - notebooks 02, 03, 04
# 02: df.head() tables only (no charts in notebook)
# 03: df.head() tables only (no charts in notebook)
# 04: metricas comparativas (print statements) -> shown as metric cards + info table
#     No charts in notebook 04 - shown as text/table content
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_cache import df_nltk, df_spacy, nltk_tags, spacy_upos, spacy_fine

dash.register_page(__name__, path="/pos-distributions", name="POS Tags", order=2)

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

# -- spaCy figures (notebook 03 result) ----------------------------------------
_upos_s = pd.Series(spacy_upos).value_counts().reset_index()
_upos_s.columns = ["Tag", "Count"]
_fine_s = pd.Series(spacy_fine).value_counts().head(20).reset_index()
_fine_s.columns = ["Tag", "Count"]

fig_spacy_bar = fig_base(px.bar(_upos_s, x="Count", y="Tag", orientation="h",
    color="Count", color_continuous_scale="Purples",
    labels={"Count": "Tokens", "Tag": ""}))
fig_spacy_bar.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))

fig_spacy_pie = fig_base(px.pie(_upos_s, names="Tag", values="Count",
    color_discrete_sequence=PAL, hole=0.4))
fig_spacy_pie.update_layout(legend=dict(font=dict(size=9)))

fig_fine = fig_base(px.bar(_fine_s, x="Tag", y="Count",
    color="Count", color_continuous_scale="Purples",
    labels={"Tag": "Tag Penn", "Count": "Frecuencia"}))
fig_fine.update_layout(coloraxis_showscale=False)

# Heatmap spaCy por genero
_gps = []
for _, row in df_spacy.iterrows():
    for _, upos, _, _ in row["pos_tags_spacy"]:
        _gps.append({"Genre": row["Genre"], "POS": upos})
_gps_df = pd.DataFrame(_gps)
_top10 = _upos_s.head(10)["Tag"].tolist()
_hp = _gps_df[_gps_df["POS"].isin(_top10)].groupby(["Genre","POS"]).size().reset_index(name="n")
_hp_piv = _hp.pivot(index="Genre", columns="POS", values="n").fillna(0)
fig_spacy_heat = go.Figure(data=go.Heatmap(
    z=_hp_piv.values, x=_hp_piv.columns.tolist(), y=_hp_piv.index.tolist(),
    colorscale="Purples", showscale=True))
fig_spacy_heat.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG,
    font_color=FONT, font_family="Inter", margin=dict(l=10,r=10,t=10,b=10))

# -- NLTK figures (notebook 02 result) -----------------------------------------
_nltk_s = pd.Series(nltk_tags).value_counts().reset_index()
_nltk_s.columns = ["Tag", "Count"]
_nltk20 = _nltk_s.head(20)

fig_nltk_bar = fig_base(px.bar(_nltk20, x="Count", y="Tag", orientation="h",
    color="Count", color_continuous_scale="Purples",
    labels={"Count": "Tokens", "Tag": ""}))
fig_nltk_bar.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))

fig_nltk_pie = fig_base(px.pie(_nltk20.head(15), names="Tag", values="Count",
    color_discrete_sequence=px.colors.qualitative.Plotly, hole=0.4))
fig_nltk_pie.update_layout(legend=dict(font=dict(size=9)))

_gpn = []
for _, row in df_nltk.iterrows():
    for _, tag in row["pos_tags"]:
        _gpn.append({"Genre": row["Genre"], "Tag": tag})
_gpn_df = pd.DataFrame(_gpn)
_hn = _gpn_df[_gpn_df["Tag"].isin(_nltk20.head(10)["Tag"])].groupby(["Genre","Tag"]).size().reset_index(name="n")
_hn_piv = _hn.pivot(index="Genre", columns="Tag", values="n").fillna(0)
fig_nltk_heat = go.Figure(data=go.Heatmap(
    z=_hn_piv.values, x=_hn_piv.columns.tolist(), y=_hn_piv.index.tolist(),
    colorscale="Purples", showscale=True))
fig_nltk_heat.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG,
    font_color=FONT, font_family="Inter", margin=dict(l=10,r=10,t=10,b=10))

# -- Comparacion figures (notebook 04) -----------------------------------------
# Notebook 04 has NO charts - only print() metrics and markdown text
# We show: metric cards + comparison bar + info table
_mapping = {
    "NN":"NOUN","NNS":"NOUN","NNP":"PROPN","NNPS":"PROPN",
    "VB":"VERB","VBD":"VERB","VBG":"VERB","VBN":"VERB","VBP":"VERB","VBZ":"VERB",
    "MD":"AUX","JJ":"ADJ","JJR":"ADJ","JJS":"ADJ",
    "RB":"ADV","RBR":"ADV","RBS":"ADV",
    "PRP":"PRON","PRP$":"PRON","WP":"PRON","WP$":"PRON",
    "DT":"DET","IN":"ADP","CC":"CCONJ","CD":"NUM","UH":"INTJ","RP":"PART","TO":"PART",
}
_nltk_mapped = pd.Series([_mapping.get(t,"OTHER") for t in nltk_tags]).value_counts()
_spacy_vc    = pd.Series(spacy_upos).value_counts()
_cats        = sorted(set(_nltk_mapped.index) | set(_spacy_vc.index))

fig_compare = go.Figure()
fig_compare.add_trace(go.Bar(name="NLTK (mapped)", x=_cats,
    y=[_nltk_mapped.get(c,0) for c in _cats], marker_color="#6A1B9A", opacity=0.8))
fig_compare.add_trace(go.Bar(name="spaCy (Universal)", x=_cats,
    y=[_spacy_vc.get(c,0) for c in _cats], marker_color="#CE93D8", opacity=0.8))
fig_compare.update_layout(barmode="group", plot_bgcolor=PLOT, paper_bgcolor=BG,
    font_color=FONT, font_family="Inter", margin=dict(l=10,r=10,t=10,b=10),
    legend=dict(font=dict(size=10)))
fig_compare.update_xaxes(gridcolor=GRID); fig_compare.update_yaxes(gridcolor=GRID)

# Notebook 04 conclusions table
_conclusions = [
    ("spaCy ventaja", "17 categorias Universal POS mas interpretables para generos"),
    ("spaCy ventaja", "Separa VERB de AUX - densidad verbal real"),
    ("spaCy ventaja", "Identifica PROPN - relevante en rap/hip-hop"),
    ("spaCy ventaja", "Incluye lematizacion - vocabulario unico"),
    ("spaCy ventaja", "INTJ captura exclamaciones tipicas (oh, yeah, whoa)"),
    ("NLTK ventaja",  "Distingue VBD vs VBZ vs VBG (tiempos verbales)"),
    ("NLTK ventaja",  "Procesamiento ~5x mas rapido"),
    ("NLTK ventaja",  "Compatibilidad con recursos linguisticos academicos"),
]
_conc_rows = [html.Tr([
    html.Td(cat, style={"fontFamily":"Inter,sans-serif","fontSize":"0.75rem","padding":"0.3rem 0.5rem",
        "border":"1px solid #D0E8F5","color":"#6A1B9A" if "spaCy" in cat else "#AB47BC","fontWeight":"600"}),
    html.Td(desc,style={"fontFamily":"Inter,sans-serif","fontSize":"0.78rem","padding":"0.3rem 0.5rem",
        "border":"1px solid #D0E8F5","color":FONT}),
]) for cat, desc in _conclusions]

# -- Tab views ------------------------------------------------------------------
_view_spacy = html.Div([
    dbc.Row([
        dbc.Col(html.Div([html.Div(f"{len(spacy_upos):,}", className="metric-value"), html.Div("Tokens totales spaCy", className="metric-label")], className="metric-card"), xs=6, md=4),
        dbc.Col(html.Div([html.Div(str(len(set(spacy_upos))), className="metric-value"), html.Div("Categorias Universal POS", className="metric-label")], className="metric-card"), xs=6, md=4),
        dbc.Col(html.Div([html.Div(str(len(set(spacy_fine))), className="metric-value"), html.Div("Tags Penn via spaCy", className="metric-label")], className="metric-card"), xs=6, md=4),
    ], className="g-2", style={"marginBottom":"1.25rem"}),
    dbc.Row([
        dbc.Col(card("Frecuencia por Categoria Universal POS", dcc.Graph(figure=fig_spacy_bar, config={"displayModeBar":False}, style={"height":"340px"})), md=6),
        dbc.Col(card("Proporcion de Categorias POS",           dcc.Graph(figure=fig_spacy_pie, config={"displayModeBar":False}, style={"height":"340px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Top 20 Tags Fine-Grained (Penn Treebank via spaCy)", dcc.Graph(figure=fig_fine,       config={"displayModeBar":False}, style={"height":"270px"})), md=6),
        dbc.Col(card("Heatmap POS por Genero (Top 10 tags)",               dcc.Graph(figure=fig_spacy_heat, config={"displayModeBar":False}, style={"height":"270px"})), md=6),
    ], className="g-0"),
])

_view_nltk = html.Div([
    dbc.Row([
        dbc.Col(html.Div([html.Div(f"{len(nltk_tags):,}", className="metric-value"), html.Div("Tokens totales NLTK", className="metric-label")], className="metric-card"), xs=6, md=4),
        dbc.Col(html.Div([html.Div(str(len(set(nltk_tags))), className="metric-value"), html.Div("Tags unicos Penn Treebank", className="metric-label")], className="metric-card"), xs=6, md=4),
        dbc.Col(html.Div([html.Div(_nltk_s.iloc[0]["Tag"], className="metric-value", style={"fontSize":"1.4rem"}), html.Div("Tag mas frecuente", className="metric-label")], className="metric-card"), xs=6, md=4),
    ], className="g-2", style={"marginBottom":"1.25rem"}),
    dbc.Row([
        dbc.Col(card("Top 20 Tags Penn Treebank - NLTK", dcc.Graph(figure=fig_nltk_bar, config={"displayModeBar":False}, style={"height":"360px"})), md=6),
        dbc.Col(card("Proporcion Top 15 Tags",           dcc.Graph(figure=fig_nltk_pie, config={"displayModeBar":False}, style={"height":"360px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Heatmap Top 10 Tags por Genero - NLTK", dcc.Graph(figure=fig_nltk_heat, config={"displayModeBar":False}, style={"height":"280px"})), md=12),
    ], className="g-0"),
])

_view_compare = html.Div([
    dbc.Row([
        dbc.Col(html.Div([html.Div(str(len(set(nltk_tags))),  className="metric-value"), html.Div("Tags unicos NLTK", className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(str(len(set(spacy_upos))), className="metric-value"), html.Div("Tags unicos spaCy Universal", className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(f"{len(nltk_tags):,}",  className="metric-value", style={"fontSize":"1.4rem"}), html.Div("Total tokens NLTK",  className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(f"{len(spacy_upos):,}", className="metric-value", style={"fontSize":"1.4rem"}), html.Div("Total tokens spaCy", className="metric-label")], className="metric-card"), xs=6, md=3),
    ], className="g-2", style={"marginBottom":"1.25rem"}),
    dbc.Row([
        dbc.Col(card("NLTK vs spaCy - Universal POS (NLTK mapeado a Universal)",
            dcc.Graph(figure=fig_compare, config={"displayModeBar":False}, style={"height":"300px"})), md=12),
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            html.Div("Comparacion de uso - Notebook 04 (metricas y conclusiones)", className="section-title"),
            html.Div([
                html.P("NLTK proceso el corpus en ~1 min. spaCy tardo ~5 min (5x mas lento) pero ejecuta "
                       "tokenizacion + POS tagging + dependency parsing + lematizacion + NER en un solo pipeline.",
                    style={"fontFamily":"Inter,sans-serif","fontSize":"0.82rem","color":FONT,"marginBottom":"0.75rem","lineHeight":"1.6"}),
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Modelo", style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A"}),
                        html.Th("Observacion", style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A"}),
                    ])),
                    html.Tbody(_conc_rows),
                ], style={"width":"100%","borderCollapse":"collapse"}),
            ]),
        ], className="card-panel", md=12),
    ], className="g-0"),
])

# -- Layout ---------------------------------------------------------------------
layout = html.Div([
    html.H2("POS Tags - Distribuciones"),
    html.P("Categorias gramaticales con NLTK (notebooks 02-03) y comparacion de modelos (notebook 04)",
           className="page-sub"),
    dcc.Tabs(id="pos-tabs", value="spacy", children=[
        dcc.Tab(label="spaCy (Universal POS)", value="spacy",
            style={"fontFamily":"Inter","background":"#FCF0FF","color":"#5A7A8A","border":"1px solid #D1A8E8"},
            selected_style={"fontFamily":"Inter","background":"#FFFFFF","color":"#6A1B9A","borderBottom":"2px solid #6A1B9A","fontWeight":"600"}),
        dcc.Tab(label="NLTK (Penn Treebank)", value="nltk",
            style={"fontFamily":"Inter","background":"#FCF0FF","color":"#5A7A8A","border":"1px solid #D1A8E8"},
            selected_style={"fontFamily":"Inter","background":"#FFFFFF","color":"#8E24AA","borderBottom":"2px solid #8E24AA","fontWeight":"600"}),
        dcc.Tab(label="Comparacion NLTK vs spaCy", value="compare",
            style={"fontFamily":"Inter","background":"#FCF0FF","color":"#5A7A8A","border":"1px solid #D1A8E8"},
            selected_style={"fontFamily":"Inter","background":"#FFFFFF","color":"#9C27B0","borderBottom":"2px solid #9C27B0","fontWeight":"600"}),
    ], style={"marginBottom":"0.5rem"}),
    html.Div(id="pos-tab-content"),
])

@callback(Output("pos-tab-content","children"), Input("pos-tabs","value"))
def switch_tab(tab):
    if tab == "nltk":    return _view_nltk
    if tab == "compare": return _view_compare
    return _view_spacy
