"""pages/corpus.py — Corpus & Pipeline MongoDB"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from data import (base_layout, PALETTE, GENRE_COLORS, GENRES,
                  get_corpus_completeness, get_pos_metrics,
                  get_language_dist, get_pos_radar)

dash.register_page(__name__, path="/corpus", title="Corpus & MongoDB")

def card(title, tag, cid, tall=False, xl=False, full=False):
    body = "chart-body" + (" chart-tall" if tall else "") + (" chart-xl" if xl else "")
    return html.Div(className=f"chart-card{'  full-width' if full else ''}", children=[
        html.Div(className="chart-header", children=[html.H3(title), html.Span(tag, className="chart-tag")]),
        dcc.Graph(id=cid, className=body, config={"displayModeBar": False}),
    ])

def pipe_step(icon, label, sub, highlight=False):
    cls = "pipe-step" + (" pipe-highlight" if highlight else "")
    return html.Div(className=cls, children=[
        html.Div(icon, className="pipe-icon"),
        html.Div(label, className="pipe-label"),
        html.Div(sub,   className="pipe-sub"),
    ])

layout = html.Div(className="page-inner", children=[
    html.Div(className="section-intro", children=[
        html.Div(children=[
            html.H2("Corpus & Pipeline MongoDB"),
            html.P("Flujo completo desde Kaggle y Genius API hasta MongoDB. "
                   "Esquema documental con Lyrics, POS Tags (NLTK + spaCy), "
                   "embeddings Word2Vec/BERT y métricas morfosintácticas por canción."),
        ]),
    ]),

    # Pipeline + completitud
    html.Div(className="grid-2", children=[
        html.Div(className="chart-card", children=[
            html.Div(className="chart-header", children=[
                html.H3("Pipeline de Datos"),
                html.Span("Flujo de procesamiento completo", className="chart-tag"),
            ]),
            html.Div(className="pipeline-diagram", children=[
                pipe_step("📦","Kaggle CSV",   "~7,000 canciones"),
                html.Div("→", className="pipe-arrow"),
                pipe_step("🔍","Genius API",   "Scraping"),
                html.Div("→", className="pipe-arrow"),
                pipe_step("🗄️","MongoDB",      "musica.canciones"),
                html.Div("→", className="pipe-arrow"),
                pipe_step("⚙️","POS Tags",     "NLTK + spaCy"),
                html.Div("→", className="pipe-arrow"),
                pipe_step("🧠","Embeddings",   "W2V + BERT", highlight=True),
                html.Div("→", className="pipe-arrow"),
                pipe_step("📊","Métricas",     "18 indicadores", highlight=True),
            ]),
        ]),
        card("Estado de Enriquecimiento del Corpus",
             "Completitud por campo",
             "fig-corpus-status"),
    ]),

    html.Div(className="grid-2", children=[
        card("Métricas Morfosintácticas por Género",
             "Densidad léxica · TTR · palabras promedio",
             "fig-pos-metrics", tall=True),
        card("Distribución de Idiomas",
             "Detección automática via Genius API",
             "fig-languages", tall=True),
    ]),

    card("Ratios POS por Género — Radar",
         "Sustantivos · Verbos · Adjetivos · Adverbios · Pronombres",
         "fig-pos-radar", tall=True, full=True),
])

# ── Callbacks ──────────────────────────────────────────────────────────────────
@callback(Output("fig-corpus-status","figure"), Input("fig-corpus-status","id"))
def fig_status(_):
    df = get_corpus_completeness()
    if df.empty:
        return go.Figure()
    colors = [PALETTE["cool"] if p==100 else
              PALETTE["accent"] if p>=85 else PALETTE["warm"]
              for p in df["pct"]]
    fig = go.Figure(go.Bar(
        x=df["pct"], y=df["field"], orientation="h",
        marker=dict(color=colors, opacity=.88),
        text=[f"{p}%" for p in df["pct"]], textposition="inside",
        textfont=dict(color="#0d0e12",size=11,family="DM Mono, monospace"),
        hovertemplate="<b>%{y}</b><br>%{x}% completado<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=10,r=30,b=40,l=130),
        xaxis=dict(range=[0,110],
                   title=dict(text="% Completado",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        yaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["text"])),
    ))
    return fig

@callback(Output("fig-pos-metrics","figure"), Input("fig-pos-metrics","id"))
def fig_pos_metrics(_):
    df = get_pos_metrics()
    if df.empty:
        return go.Figure()
    fig = go.Figure([
        go.Bar(name="Densidad Léxica", x=df["genre"], y=df["density"],
               marker=dict(color=PALETTE["accent"]+"cc"),
               hovertemplate="<b>%{x}</b><br>Densidad: %{y:.3f}<extra></extra>"),
        go.Bar(name="TTR", x=df["genre"], y=df["ttr"],
               marker=dict(color=PALETTE["warm"]+"cc"),
               hovertemplate="<b>%{x}</b><br>TTR: %{y:.3f}<extra></extra>"),
    ])
    fig.update_layout(**base_layout(
        barmode="group",
        legend=dict(orientation="h",y=-0.25,font=dict(size=10,color=PALETTE["muted"]),bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["text"])),
        yaxis=dict(gridcolor=PALETTE["border"],zeroline=False,tickfont=dict(color=PALETTE["muted"])),
        margin=dict(t=10,r=20,b=70,l=50),
    ))
    return fig

@callback(Output("fig-languages","figure"), Input("fig-languages","id"))
def fig_lang(_):
    df = get_language_dist()
    if df.empty:
        return go.Figure()
    colors = [PALETTE["accent"],PALETTE["warm"],PALETTE["cool"],PALETTE["gold"],PALETTE["muted"]]
    fig = go.Figure(go.Pie(
        labels=df["lang"], values=df["count"], hole=.50,
        marker=dict(colors=colors),
        textfont=dict(color=PALETTE["text"],size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,} canciones (%{percent})<extra></extra>",
    ))
    fig.update_layout(**base_layout(margin=dict(t=20,r=20,b=20,l=20),showlegend=True))
    return fig

@callback(Output("fig-pos-radar","figure"), Input("fig-pos-radar","id"))
def fig_radar(_):
    df = get_pos_radar()
    if df.empty:
        return go.Figure()
    metrics = df["metric"].unique().tolist()
    closed  = metrics + [metrics[0]]
    fig = go.Figure()
    for g in GENRES:
        sub = df[df["genre"]==g].set_index("metric")
        if sub.empty: continue
        vals = [float(sub.loc[m,"value"]) if m in sub.index else 0 for m in metrics]
        vals = vals + [vals[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=closed, mode="lines+markers", name=g,
            fill="toself",
            line=dict(color=GENRE_COLORS.get(g,PALETTE["accent"]),width=2),
            fillcolor=GENRE_COLORS.get(g,PALETTE["accent"])+"22",
            marker=dict(color=GENRE_COLORS.get(g,PALETTE["accent"]),size=5),
            hovertemplate=f"<b>{g}</b> · %{{theta}}: %{{r:.4f}}<extra></extra>",
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'DM Mono', monospace", color=PALETTE["text"]),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True,range=[0,.45],gridcolor=PALETTE["border"],
                            linecolor=PALETTE["border"],tickfont=dict(color=PALETTE["muted"],size=9)),
            angularaxis=dict(gridcolor=PALETTE["border"],linecolor=PALETTE["border"],
                             tickfont=dict(color=PALETTE["text"],size=10)),
        ),
        legend=dict(orientation="h",y=-0.05,bgcolor="rgba(0,0,0,0)",
                    font=dict(color=PALETTE["muted"],size=10)),
        margin=dict(t=20,r=60,b=40,l=60),
        hoverlabel=dict(bgcolor="#21232e",font=dict(color=PALETTE["text"],size=11)),
    )
    return fig
