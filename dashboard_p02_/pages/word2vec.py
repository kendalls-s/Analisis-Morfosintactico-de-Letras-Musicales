"""pages/word2vec.py — Word2Vec: Representaciones Estáticas"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import numpy as np
from data import (base_layout, PALETTE, GENRE_COLORS, GENRES, WORD_PAIRS,
                  get_w2v_similarity, get_w2v_vocab_top, get_w2v_vocab_size,
                  get_w2v_tsne, get_w2v_analogies, get_w2v_genre_similarity)

dash.register_page(__name__, path="/word2vec", title="Word2Vec")

def card(title, tag, cid, tall=False, xl=False, full=False, span2=False):
    extra = (" full-width" if full else "") + (" span-2" if span2 else "")
    body  = "chart-body" + (" chart-tall" if tall else "") + (" chart-xl" if xl else "")
    return html.Div(className=f"chart-card{extra}", children=[
        html.Div(className="chart-header", children=[html.H3(title), html.Span(tag, className="chart-tag")]),
        dcc.Graph(id=cid, className=body, config={"displayModeBar": False}),
    ])

layout = html.Div(className="page-inner", children=[
    html.Div(className="section-intro", children=[
        html.Div(children=[
            html.H2("Representaciones Estáticas con Word2Vec"),
            html.P("Modelos CBOW y Skip-Gram entrenados sobre el corpus musical. "
                   "Vectores de 100 dimensiones que capturan relaciones semánticas: "
                   "campos léxicos, analogías y similitud entre géneros."),
        ]),
        html.Div(className="model-badges", children=[
            html.Div(className="model-badge", children=["CBOW",     html.Span("vector_size=100 · window=5")]),
            html.Div(className="model-badge", children=["Skip-Gram",html.Span("min_count=5 · epochs=20")]),
        ]),
    ]),

    # Fila 1: similitud pares + vocab top
    html.Div(className="grid-2", children=[
        card("Similitud Coseno — Pares de Palabras", "Por género musical", "fig-w2v-sim", tall=True),
        card("Top Vocabulario por Género", "Skip-Gram · Top 8 lemas", "fig-w2v-vocab", tall=True),
    ]),

    # t-SNE full width
    card("Proyección t-SNE — Embeddings Word2Vec",
         "100 dim → 2D · coloreado por género", "fig-w2v-tsne", xl=True, full=True),

    # Similitud entre géneros
    card("Similitud entre Géneros — Centroides Word2Vec",
         "Coseno entre vector promedio de cada género",
         "fig-w2v-genre-sim", tall=True, full=True),

    # Analogías + vocab size
    html.Div(className="grid-2", children=[
        card("Analogías Vectoriales",  "Operaciones semánticas",        "fig-w2v-analogies"),
        card("Vocabulario por Género", "CBOW vs Skip-Gram (palabras únicas)", "fig-w2v-vocab-size"),
    ]),
])

# ── Callbacks ──────────────────────────────────────────────────────────────────
@callback(Output("fig-w2v-sim","figure"), Input("fig-w2v-sim","id"))
def fig_sim(_):
    df = get_w2v_similarity()
    cs = [[0,"#0d0e12"],[.3,"#3d3580"],[.6,PALETTE["accent"]],[1,"#c9c0ff"]]
    fig = go.Figure(go.Heatmap(
        z=df.values.tolist(), x=GENRES, y=WORD_PAIRS, colorscale=cs,
        hovertemplate="<b>%{y}</b> · %{x}<br>Similitud: %{z:.3f}<extra></extra>",
        showscale=True, colorbar=dict(tickfont=dict(color=PALETTE["muted"],size=9),thickness=12),
        text=[[f"{v:.3f}" for v in row] for row in df.values],
        texttemplate="%{text}", textfont=dict(size=9,color="white"),
    ))
    fig.update_layout(**base_layout(margin=dict(t=10,r=70,b=70,l=80)))
    return fig

@callback(Output("fig-w2v-vocab","figure"), Input("fig-w2v-vocab","id"))
def fig_vocab(_):
    vocab = get_w2v_vocab_top()
    fig   = go.Figure()
    for i, g in enumerate(GENRES):
        fig.add_trace(go.Bar(
            name=g, x=vocab.get(g,[]), y=[1]*8,
            marker=dict(color=GENRE_COLORS.get(g,PALETTE["accent"])),
            visible=True if i==0 else "legendonly",
            hovertemplate=f"<b>%{{x}}</b> · {g}<extra></extra>",
        ))
    fig.update_layout(**base_layout(
        barmode="group",
        xaxis=dict(tickangle=-30,gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["text"])),
        yaxis=dict(visible=False),
        legend=dict(orientation="h",y=-0.30,font=dict(color=PALETTE["muted"],size=10),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=10,r=20,b=80,l=30),
    ))
    return fig

@callback(Output("fig-w2v-tsne","figure"), Input("fig-w2v-tsne","id"))
def fig_tsne(_):
    df = get_w2v_tsne()
    fig = go.Figure()
    for g in GENRES:
        sub = df[df["genre"]==g]
        fig.add_trace(go.Scatter(
            x=sub["x"],y=sub["y"],mode="markers",name=g,
            marker=dict(color=GENRE_COLORS.get(g,PALETTE["accent"]),size=6,opacity=.75,line=dict(width=0)),
            hovertemplate=f"<b>{g}</b><extra></extra>",
        ))
    fig.update_layout(**base_layout(
        legend=dict(orientation="h",y=-0.08,font=dict(color=PALETTE["muted"],size=10),bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title=dict(text="t-SNE 1",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        yaxis=dict(title=dict(text="t-SNE 2",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        margin=dict(t=10,r=20,b=60,l=55),
    ))
    return fig

@callback(Output("fig-w2v-genre-sim","figure"), Input("fig-w2v-genre-sim","id"))
def fig_genre_sim(_):
    df = get_w2v_genre_similarity()
    gs = df.columns.tolist()
    cs = [[0,"#0d0e12"],[.4,"#2a1f6e"],[.7,PALETTE["accent"]],[1,"#c9c0ff"]]
    fig = go.Figure(go.Heatmap(
        z=df.values.tolist(), x=gs, y=gs, colorscale=cs,
        hovertemplate="<b>%{y}</b> ↔ <b>%{x}</b><br>Similitud: %{z:.3f}<extra></extra>",
        showscale=True, colorbar=dict(tickfont=dict(color=PALETTE["muted"],size=9),thickness=12),
        text=[[f"{v:.3f}" for v in row] for row in df.values],
        texttemplate="%{text}", textfont=dict(size=9,color="white"),
    ))
    fig.update_layout(**base_layout(margin=dict(t=10,r=70,b=70,l=90)))
    return fig

@callback(Output("fig-w2v-analogies","figure"), Input("fig-w2v-analogies","id"))
def fig_analogies(_):
    df = get_w2v_analogies()
    fig = go.Figure(go.Bar(
        x=df["score"], y=df["op"], orientation="h",
        text=[f"→ {r}" for r in df["result"]],
        textposition="outside", textfont=dict(color=PALETTE["cool"],size=10),
        marker=dict(color=df["score"].tolist(),
                    colorscale=[[0,PALETTE["accent"]+"55"],[1,PALETTE["accent"]]],
                    showscale=False),
        hovertemplate="<b>%{y}</b><br>→ %{text}<br>Score: %{x:.3f}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=10,r=100,b=40,l=185),
        xaxis=dict(range=[0,.9],gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["muted"])),
        yaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["text"])),
    ))
    return fig

@callback(Output("fig-w2v-vocab-size","figure"), Input("fig-w2v-vocab-size","id"))
def fig_vocab_size(_):
    df = get_w2v_vocab_size()
    if df.empty:
        return go.Figure()
    fig = go.Figure([
        go.Bar(name="CBOW",      x=df["genre"],y=df["cbow"],
               marker=dict(color=PALETTE["warm"]+"cc"),
               hovertemplate="<b>%{x}</b><br>CBOW: %{y:,}<extra></extra>"),
        go.Bar(name="Skip-Gram", x=df["genre"],y=df["sg"],
               marker=dict(color=PALETTE["accent"]+"cc"),
               hovertemplate="<b>%{x}</b><br>Skip-Gram: %{y:,}<extra></extra>"),
    ])
    fig.update_layout(**base_layout(
        barmode="group",
        yaxis=dict(title=dict(text="Palabras únicas",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        xaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["text"])),
        legend=dict(orientation="h",y=-0.25,font=dict(size=10,color=PALETTE["muted"]),bgcolor="rgba(0,0,0,0)"),
    ))
    return fig
