"""pages/bert.py — BERT: Embeddings Contextuales"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from data import (base_layout, PALETTE, GENRE_COLORS, GENRES, POLY_WORDS,
                  get_bert_polysemy, get_bert_tsne, get_bert_mlm,
                  get_bert_cohesion, get_bert_genre_similarity)

dash.register_page(__name__, path="/bert", title="BERT")

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
            html.H2("Embeddings Contextuales con BERT"),
            html.P([
                "Modelo ", html.Code("bert-base-uncased"),
                " · 768 dimensiones. La misma palabra recibe representaciones distintas "
                "según su contexto en la letra — el rasgo clave frente a Word2Vec.",
            ]),
        ]),
        html.Div(className="model-badges", children=[
            html.Div(className="model-badge", children=["bert-base-uncased", html.Span("12 capas · 768d · ~420 MB")]),
            html.Div(className="model-badge", children=["CLS Token",         html.Span("Representación global de canción")]),
        ]),
    ]),

    # Polisemia + frecuencia palabras
    html.Div(className="grid-3", children=[
        card("Polisemia Contextual — Similitud por Palabra",
             "Misma palabra, distintos géneros y contextos",
             "fig-bert-polysemy", tall=True, span2=True),
        card("Frecuencia de Palabras Analizadas",
             "Apariciones en el corpus",
             "fig-bert-words", tall=True),
    ]),

    # t-SNE full width
    card("Proyección t-SNE — Embeddings BERT [CLS]",
         "768 dimensiones → 2D · canciones coloreadas por género",
         "fig-bert-tsne", xl=True, full=True),

    # Similitud entre géneros
    card("Similitud entre Géneros — Centroides BERT [CLS]",
         "Coseno entre centroide de embeddings por género",
         "fig-bert-genre-sim", tall=True, full=True),

    # MLM + cohesión
    html.Div(className="grid-2", children=[
        card("Masked Language Model — Top Predicciones",
             "P(token | plantilla de letra musical)",
             "fig-bert-mlm", tall=True),
        card("Cohesión Semántica Intra-Género",
             "Similitud coseno BERT al centroide del género",
             "fig-bert-cohesion", tall=True),
    ]),
])

# ── Callbacks ──────────────────────────────────────────────────────────────────
@callback(Output("fig-bert-polysemy","figure"), Input("fig-bert-polysemy","id"))
def fig_polysemy(_):
    df   = get_bert_polysemy()
    pivot = df.pivot(index="word", columns="genre", values="similarity")
    # solo columnas que existen
    cols = [g for g in GENRES if g in pivot.columns]
    pivot = pivot[cols]
    cs = [[0,"#0d0e12"],[.3,"#1f4a40"],[.7,PALETTE["cool"]],[1,"#c0fff5"]]
    fig = go.Figure(go.Heatmap(
        z=pivot.values.tolist(), x=cols, y=POLY_WORDS, colorscale=cs,
        hovertemplate='<b>"%{y}"</b> en %{x}<br>Similitud: %{z:.3f}<extra></extra>',
        showscale=True, colorbar=dict(tickfont=dict(color=PALETTE["muted"],size=9),thickness=12),
        text=[[f"{v:.3f}" for v in row] for row in pivot.values],
        texttemplate="%{text}", textfont=dict(size=9,color="white"),
    ))
    fig.update_layout(**base_layout(margin=dict(t=10,r=70,b=60,l=65)))
    return fig

@callback(Output("fig-bert-words","figure"), Input("fig-bert-words","id"))
def fig_words(_):
    # Frecuencias reales de las palabras polisémicas en el corpus
    from data import _col
    freqs = []
    for w in POLY_WORDS:
        n = _col().count_documents({"Lyrics": {"$regex": w, "$options": "i"}})
        freqs.append(n)
    fig = go.Figure(go.Bar(
        x=freqs, y=POLY_WORDS, orientation="h",
        marker=dict(color=PALETTE["cool"]+"cc"),
        hovertemplate="<b>%{y}</b><br>%{x:,} canciones<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=10,r=30,b=40,l=60),
        xaxis=dict(title=dict(text="Canciones que contienen la palabra",
                              font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        yaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["text"])),
    ))
    return fig

@callback(Output("fig-bert-tsne","figure"), Input("fig-bert-tsne","id"))
def fig_tsne(_):
    df = get_bert_tsne()
    fig = go.Figure()
    for g in GENRES:
        sub = df[df["genre"]==g]
        fig.add_trace(go.Scatter(
            x=sub["x"],y=sub["y"],mode="markers",name=g,
            marker=dict(color=GENRE_COLORS.get(g,PALETTE["accent"]),size=7,opacity=.82,line=dict(width=0)),
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

@callback(Output("fig-bert-genre-sim","figure"), Input("fig-bert-genre-sim","id"))
def fig_genre_sim(_):
    df = get_bert_genre_similarity()
    gs = df.columns.tolist()
    cs = [[0,"#0d0e12"],[.4,"#1f4a40"],[.7,PALETTE["cool"]],[1,"#c0fff5"]]
    fig = go.Figure(go.Heatmap(
        z=df.values.tolist(), x=gs, y=gs, colorscale=cs,
        hovertemplate="<b>%{y}</b> ↔ <b>%{x}</b><br>Similitud: %{z:.3f}<extra></extra>",
        showscale=True, colorbar=dict(tickfont=dict(color=PALETTE["muted"],size=9),thickness=12),
        text=[[f"{v:.3f}" for v in row] for row in df.values],
        texttemplate="%{text}", textfont=dict(size=9,color="white"),
    ))
    fig.update_layout(**base_layout(margin=dict(t=10,r=70,b=70,l=90)))
    return fig

@callback(Output("fig-bert-mlm","figure"), Input("fig-bert-mlm","id"))
def fig_mlm(_):
    mlm = get_bert_mlm()
    tpl, preds = next(iter(mlm.items()))
    words = [p[0] for p in preds]; probs = [p[1] for p in preds]
    fig = go.Figure(go.Bar(
        x=probs, y=words, orientation="h",
        marker=dict(color=PALETTE["gold"]+"cc"),
        hovertemplate="<b>[MASK] → %{y}</b><br>P = %{x:.3f}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=40,r=30,b=40,l=75),
        xaxis=dict(range=[0,max(probs)*1.35],
                   title=dict(text="Probabilidad",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        yaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["text"])),
        annotations=[dict(text=f"<i>{tpl.replace('[MASK]','[M]')}</i>",
                          x=.5,y=1.1,xref="paper",yref="paper",
                          font=dict(size=10,color=PALETTE["muted"]),showarrow=False)],
    ))
    return fig

@callback(Output("fig-bert-cohesion","figure"), Input("fig-bert-cohesion","id"))
def fig_cohesion(_):
    df = get_bert_cohesion()
    fig = go.Figure()
    for g in GENRES:
        sub = df[df["genre"]==g]["similarity"].tolist()
        if not sub: continue
        fig.add_trace(go.Violin(
            y=sub, name=g, box_visible=True, meanline_visible=True,
            line_color=GENRE_COLORS.get(g,PALETTE["accent"]),
            fillcolor=GENRE_COLORS.get(g,PALETTE["accent"])+"33",
            hovertemplate=f"<b>{g}</b><br>Similitud: %{{y:.3f}}<extra></extra>",
        ))
    fig.update_layout(**base_layout(
        showlegend=False,
        yaxis=dict(title=dict(text="Similitud coseno al centroide",
                              font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        xaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["text"])),
        margin=dict(t=10,r=20,b=50,l=60),
    ))
    return fig
