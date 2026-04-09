"""pages/overview.py — Resumen General"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from data import (base_layout, PALETTE, GENRE_COLORS, GENRES,
                  get_kpis, get_genre_distribution, get_source_split,
                  get_lyrics_length_stats, get_corpus_timeline)

dash.register_page(__name__, path="/", title="Resumen General")

def kpi(value, label, sub, accent=False):
    return html.Div(className=f"kpi-card{'  accent-card' if accent else ''}", children=[
        html.Div(value, className="kpi-val"),
        html.Div(label, className="kpi-label"),
        html.Div(sub,   className="kpi-sub"),
    ])

def chart_card(title, tag, chart_id, tall=False, full=False):
    body = "chart-body" + (" chart-tall" if tall else "")
    return html.Div(className=f"chart-card{'  full-width' if full else ''}", children=[
        html.Div(className="chart-header", children=[
            html.H3(title), html.Span(tag, className="chart-tag")]),
        dcc.Graph(id=chart_id, className=body, config={"displayModeBar": False}),
    ])

layout = html.Div(className="page-inner", children=[
    # KPIs — cargados dinámicamente desde MongoDB
    html.Div(id="kpi-row", className="kpi-row"),

    html.Div(className="grid-2", children=[
        chart_card("Distribución por Género",  "Corpus completo",  "fig-genre-dist"),
        chart_card("Canciones por Fuente",     "Kaggle vs Genius", "fig-source"),
    ]),
])

# ── Callbacks ──────────────────────────────────────────────────────────────────
@callback(Output("kpi-row","children"), Input("kpi-row","id"))
def render_kpis(_):
    k = get_kpis()
    return [
        kpi(f'{k["total"]:,}',   "Canciones Totales", "Corpus completo"),
        kpi(str(k["artists"]),   "Artistas",          "Genius Scraping + Kaggle"),
        kpi(str(k["genres"]),    "Géneros",           " · ".join(GENRES)),
        kpi(k["best_acc"],       "Mejor Accuracy",    "LR sobre BERT embeddings", accent=True),
    ]

@callback(Output("fig-genre-dist","figure"), Input("fig-genre-dist","id"))
def fig_genre(_):
    df = get_genre_distribution()
    fig = go.Figure(go.Bar(
        x=df["count"], y=df["genre"], orientation="h",
        marker=dict(color=[GENRE_COLORS.get(g, PALETTE["accent"]) for g in df["genre"]], opacity=.88),
        hovertemplate="<b>%{y}</b><br>%{x:,} canciones<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=10,r=20,b=40,l=90),
        xaxis=dict(title=dict(text="Canciones",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        yaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["text"])),
    ))
    return fig

@callback(Output("fig-source","figure"), Input("fig-source","id"))
def fig_source(_):
    df = get_source_split()
    fig = go.Figure(go.Pie(
        labels=df["source"], values=df["count"], hole=.55,
        marker=dict(colors=[PALETTE["accent"],PALETTE["warm"],PALETTE["cool"],
                            PALETTE["gold"],PALETTE["muted"]]),
        textfont=dict(color=PALETTE["text"],size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
    ))
    fig.update_layout(**base_layout(margin=dict(t=20,r=20,b=20,l=20),showlegend=True))
    return fig

@callback(Output("fig-lyrics-len","figure"), Input("fig-lyrics-len","id"))
def fig_lyrics(_):
    df = get_lyrics_length_stats()
    if df.empty:
        return go.Figure()
    fig = go.Figure()
    for _, row in df.iterrows():
        g = row["genre"]
        c = GENRE_COLORS.get(g, PALETTE["accent"])
        fig.add_trace(go.Box(
            name=g, q1=[row["q1"]], median=[row["median"]], q3=[row["q3"]],
            lowerfence=[row["lo"]], upperfence=[row["hi"]],
            marker=dict(color=c), line=dict(color=c), fillcolor=c+"33",
            hovertemplate=f"<b>{g}</b><br>Mediana: %{{median}}<br>Q1–Q3: %{{q1}}–%{{q3}}<extra></extra>",
        ))
    fig.update_layout(**base_layout(
        showlegend=False,
        yaxis=dict(title=dict(text="Palabras",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        xaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["text"])),
    ))
    return fig

@callback(Output("fig-timeline","figure"), Input("fig-timeline","id"))
def fig_timeline(_):
    df = get_corpus_timeline()
    if df.empty:
        return go.Figure()
    fig = go.Figure(go.Scatter(
        x=df["year"], y=df["count"], mode="lines", fill="tozeroy",
        line=dict(color=PALETTE["accent"],width=2), fillcolor=PALETTE["accent"]+"22",
        hovertemplate="<b>%{x}</b><br>%{y} canciones<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        xaxis=dict(title=dict(text="Año",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        yaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
    ))
    return fig
