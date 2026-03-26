# -*- coding: utf-8 -*-
# POS Tagging Dashboard - Main entry point
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="POS Tagging - Letras Musicales",
)
server = app.server

NAV_LINKS = [
    {"label": "Inicio",      "href": "/"},
    {"label": "EDA",         "href": "/eda"},
    {"label": "POS Tags",    "href": "/pos-distributions"},
    {"label": "Morfologico", "href": "/morphological"},
    {"label": "Generos",     "href": "/genre-comparison"},
    {"label": "Temporal",    "href": "/temporal-evolution"},
    {"label": "Metricas",    "href": "/metrics"},
    {"label": "Word2Vec",    "href": "/word2vec"},
    {"label": "BERT",        "href": "/bert"},
    {"label": "Comparacion", "href": "/comparacion"},
]

navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(html.Span("POS", style={
                    "fontFamily": "JetBrains Mono, monospace",
                    "fontWeight": "700",
                    "fontSize": "1.1rem",
                    "color": "#FFFFFF",
                    "background": "#6A1B9A",
                    "padding": "2px 8px",
                    "borderRadius": "4px",
                    "marginRight": "6px",
                })),
                dbc.Col(dbc.NavbarBrand("Letras Musicales", style={
                    "fontFamily": "Inter, sans-serif",
                    "fontWeight": "700",
                    "fontSize": "1.1rem",
                    "color": "#FFFFFF",
                })),
            ], align="center", className="g-1"),
            href="/", style={"textDecoration": "none"},
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavLink(
                    link["label"], href=link["href"],
                    active="exact",
                    style={
                        "fontFamily": "Inter, sans-serif",
                        "fontSize": "0.85rem",
                        "color": "#E8D5F5",
                        "padding": "0.4rem 0.8rem",
                        "borderRadius": "4px",
                    },
                )
                for link in NAV_LINKS
            ], navbar=True, className="ms-auto"),
            id="navbar-collapse",
            navbar=True,
        ),
    ], fluid=True),
    color="#6A1B9A",
    dark=True,
    sticky="top",
    style={"boxShadow": "0 3px 12px rgba(106,27,154,0.3)", "background": "linear-gradient(90deg, #4A148C 0%, #7B1FA2 50%, #AD1457 100%) !important"},
)

app.layout = html.Div(
    style={"minHeight": "100vh", "backgroundColor": "#F3E5F5"},
    children=[
        navbar,
        dbc.Container(dash.page_container, fluid=True, style={"padding": "1.5rem 2rem"}),
        html.Footer(
            dbc.Container(html.P(
                "Analisis Morfosintactico de Letras Musicales - NLTK & spaCy",
                style={"fontFamily": "JetBrains Mono, monospace", "fontSize": "0.7rem",
                       "color": "#78909C", "textAlign": "center", "margin": "0", "padding": "1.2rem 0"},
            )),
            style={"borderTop": "1px solid #D1A8E8", "marginTop": "2rem", "background": "#F3E5F5"},
        ),
    ],
)

app.index_string = """
<!DOCTYPE html>
<html>
<head>
  {%metas%}
  <title>{%title%}</title>
  {%favicon%}
  {%css%}
  <style>
    /* ===== Purple Palette ===================================
       Primary:   #4A148C (deep violet)
       Secondary: #7B1FA2 (medium purple)
       Accent:    #AB47BC (soft lilac)
       Pop:       #E91E8C (fuchsia highlight)
       Tint:      #CE93D8 (lavender)
       Bg:        #F3E5F5 (very light lavender)
       Surface:   #FFFFFF
       Border:    #D1A8E8
    ========================================================= */
    * { box-sizing: border-box; }
    body { margin:0; background:#F3E5F5; color:#2D1B45; font-family: Inter, sans-serif; }
    ::-webkit-scrollbar { width:6px; }
    ::-webkit-scrollbar-track { background:#F3E5F5; }
    ::-webkit-scrollbar-thumb { background:#CE93D8; border-radius:3px; }
    .nav-link.active { color:#FFFFFF !important; background:rgba(255,255,255,0.25) !important; border-radius:4px; }
    .nav-link:hover  { color:#FFFFFF !important; background:rgba(255,255,255,0.12) !important; border-radius:4px; }
    .card-panel {
      background:#FFFFFF;
      border:1px solid #D1A8E8;
      border-radius:10px;
      padding:1.25rem;
      margin-bottom:1.25rem;
      box-shadow:0 2px 8px rgba(106,27,154,0.08);
    }
    /* Metric cards — each gets its own gradient for variety */
    .metric-card {
      background:linear-gradient(135deg,#4A148C 0%,#7B1FA2 100%);
      border-radius:10px;
      padding:1.1rem 1.2rem;
      text-align:center;
      color:#FFFFFF;
    }
    .metric-card:nth-child(2) { background:linear-gradient(135deg,#6A1B9A 0%,#AB47BC 100%); }
    .metric-card:nth-child(3) { background:linear-gradient(135deg,#880E4F 0%,#E91E8C 100%); }
    .metric-card:nth-child(4) { background:linear-gradient(135deg,#4527A0 0%,#7C4DFF 100%); }
    .metric-value {
      font-family: JetBrains Mono, monospace;
      font-size:1.8rem;
      font-weight:700;
      color:#FFFFFF;
      line-height:1;
    }
    .metric-label {
      font-family: Inter, sans-serif;
      font-size:0.7rem;
      color:#EDE7F6;
      text-transform:uppercase;
      letter-spacing:0.08em;
      margin-top:0.35rem;
    }
    .section-title {
      font-family: Inter, sans-serif;
      font-size:0.95rem;
      font-weight:600;
      color:#6A1B9A;
      border-left:3px solid #E91E8C;
      padding-left:0.6rem;
      margin-bottom:0.9rem;
    }
    h2 { font-family:Inter,sans-serif; font-weight:700; color:#2D1B45; }
    .page-sub { font-family:JetBrains Mono,monospace; font-size:0.78rem;
                color:#7E57C2; margin-bottom:1.5rem; }
    .info-box {
      background:#EDE7F6;
      border:1px solid #CE93D8;
      border-radius:8px;
      padding:1rem 1.2rem;
      font-family:Inter,sans-serif;
      font-size:0.82rem;
      color:#2D1B45;
      line-height:1.6;
      margin-bottom:1.25rem;
    }
    .tab-content { margin-top:1rem; }
  </style>
</head>
<body>
  {%app_entry%}
  <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, port=8050)



# -*- coding: utf-8 -*-
# pages/bert.py — Notebook 10: Análisis Semántico con BERT
import warnings
import numpy as np

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

warnings.filterwarnings("ignore")

dash.register_page(__name__, path="/bert", name="BERT", title="BERT – POS Tagging")

PALETTE = ["#4A148C", "#7B1FA2", "#AB47BC", "#E91E8C", "#CE93D8",
           "#7C4DFF", "#880E4F", "#4527A0", "#AD1457", "#6A1B9A"]

# Contextos de polisemia (del notebook)
POLISEMIA = {
    "fire": [
        ("Rock",       "The guitar solo was on fire and the crowd went wild tonight"),
        ("Metal",      "Open fire on the enemy no mercy in this brutal endless war"),
        ("Folk",       "Sitting by the fire watching embers fade into the cold night"),
        ("Pop",        "Your love set fire to my heart every time you smile at me"),
        ("Hip-Hop",    "We fire back at every threat the streets keep us always ready"),
    ],
    "heart": [
        ("Pop",        "My heart beats faster every time you hold me close under stars"),
        ("Metal",      "Heart of iron soul of fire we fight until the bitter end"),
        ("Jazz",       "The heart of jazz lives in the quiet space between the notes"),
        ("Country",    "She left with a broken heart driving down an empty highway"),
        ("R&B",        "Put your heart and soul into this love it is all we have"),
    ],
    "light": [
        ("Folk",       "You are the light that guides me home through darkness every night"),
        ("Electronic", "The strobe light flashed as the DJ dropped the hardest bass drop"),
        ("Indie",      "Travel light and leave behind the weight of all your old regrets"),
        ("Rock",       "One light remains burning in the window of the house we shared"),
        ("Pop",        "She lit up the room her smile the brightest light I ever saw"),
    ],
}

MLM_FRASES = {
    "Rock":       "We will [MASK] the walls and rise above the pain tonight loud",
    "Pop":        "Your love makes my [MASK] beat faster every time we are together",
    "Hip-Hop":    "We started from the [MASK] and now the whole crew is on top",
    "Metal":      "The [MASK] descends upon the earth consuming every last bit of light",
    "Electronic": "Drop the [MASK] and let the whole crowd move to the beat now",
    "Jazz":       "Late night [MASK] fills the smoky room with memories of better days",
    "Country":    "Back home on the [MASK] watching stars from the old front porch",
    "Indie":      "She wore a [MASK] dress dancing in the rain without a care",
    "R&B":        "I want to [MASK] you close and never ever let you go tonight",
    "Folk":       "Sitting by the [MASK] singing songs my grandmother taught me young",
}

CONSULTAS_SEMANTICAS = [
    ("rebellious energy distorted guitar loud crowd anthem",  "Rock/Metal"),
    ("romantic love dancing together through the night",      "Pop/R&B"),
    ("street money power hustle grind success respect",       "Hip-Hop"),
    ("darkness chaos war evil consuming fire destruction",    "Metal"),
    ("nature river rain wind quiet peace open road home",     "Folk/Country"),
]


# ─── helpers ────────────────────────────────────────────────────────────────

def _load_bert_data():
    """Carga el corpus desde data_cache."""
    try:
        from data_cache import df_clean
        import pandas as pd
        df = df_clean[["Song", "Artist", "Genre", "Song year", "Lyrics"]].copy()
        df = df.dropna(subset=["Lyrics", "Genre"])
        df["Lyrics"] = df["Lyrics"].astype(str).str.strip()
        df = df[df["Lyrics"].str.len() > 50].reset_index(drop=True)
        conteo = df["Genre"].value_counts()
        genres = conteo[conteo >= 20].index.tolist()
        df = df[df["Genre"].isin(genres)].reset_index(drop=True)
        return df, genres, None
    except Exception as e:
        return None, None, str(e)


def _load_bert_model():
    try:
        import torch
        from transformers import AutoTokenizer, AutoModel
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        model = AutoModel.from_pretrained("bert-base-uncased").to(device)
        model.eval()
        return tokenizer, model, device, None
    except Exception as e:
        return None, None, None, str(e)


def _bert_cls_embedding(text, tokenizer, model, device):
    import torch
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128).to(device)
    with torch.no_grad():
        out = model(**inputs)
    return out.last_hidden_state[0, 0].cpu().numpy()


def _embedding_en_contexto(text, word, tokenizer, model, device):
    import torch
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128).to(device)
    with torch.no_grad():
        out = model(**inputs)
    hidden = out.last_hidden_state[0]
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    obj = word.lower()
    for i, tok in enumerate(tokens):
        clean = tok.replace("##", "").lower()
        if clean == obj or obj in clean:
            return hidden[i].cpu().numpy()
    return hidden[0].cpu().numpy()  # fallback [CLS]


def _fig_polisemia(embs_dict):
    from scipy.spatial.distance import cosine as sp_cos
    figs = {}
    for palabra, resultados in embs_dict.items():
        n = len(resultados)
        labels = [r["genre"] for r in resultados]
        sim = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                sim[i, j] = 1 - sp_cos(resultados[i]["emb"], resultados[j]["emb"])
        fig = go.Figure(go.Heatmap(
            z=sim, x=labels, y=labels,
            colorscale="RdYlGn", zmin=0.3, zmax=1.0,
            text=[[f"{sim[i,j]:.2f}" for j in range(n)] for i in range(n)],
            texttemplate="%{text}", textfont={"size": 11},
        ))
        fig.update_layout(
            title=f"Polisemia contextual — «{palabra}»<br>"
                  "<sup>Valores bajos = BERT distingue el significado según contexto</sup>",
            height=360, margin=dict(l=10, r=10, t=70, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter,sans-serif", size=11),
            xaxis=dict(tickangle=-30),
        )
        figs[palabra] = fig
    return figs


def _fig_genre_heatmap_bert(centroides):
    from scipy.spatial.distance import cosine as sp_cos
    ords = sorted(centroides)
    n    = len(ords)
    mat  = np.zeros((n, n))
    for i, g1 in enumerate(ords):
        for j, g2 in enumerate(ords):
            mat[i, j] = 1 - sp_cos(centroides[g1], centroides[g2])
    fig = go.Figure(go.Heatmap(
        z=mat, x=ords, y=ords, colorscale="RdPu",
        zmin=mat[~np.eye(n, dtype=bool)].min(), zmax=1.0,
        text=[[f"{mat[i,j]:.3f}" for j in range(n)] for i in range(n)],
        texttemplate="%{text}", textfont={"size": 10},
    ))
    fig.update_layout(
        title="Similitud coseno entre géneros (centroides BERT [CLS])",
        height=420, margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter,sans-serif", size=12),
        xaxis=dict(tickangle=-30),
    )
    return fig


def _fig_mlm(mlm_results, genres):
    traces, genre_list = [], [g for g in genres if g in mlm_results]
    n_cols = 2
    n_rows = (len(genre_list) + 1) // 2
    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=[f"{g}" for g in genre_list],
        horizontal_spacing=0.12, vertical_spacing=0.12,
    )
    for idx, genre in enumerate(genre_list):
        row = idx // n_cols + 1
        col = idx % n_cols + 1
        data = mlm_results[genre]
        words = data["words"][:5]
        probs = data["probs"][:5]
        color = PALETTE[idx % len(PALETTE)]
        fig.add_trace(go.Bar(
            x=probs[::-1], y=words[::-1], orientation="h",
            marker_color=color, name=genre, showlegend=False,
            text=[f"{p:.3f}" for p in probs[::-1]], textposition="outside",
        ), row=row, col=col)
    fig.update_layout(
        title="BERT MLM — Predicciones de [MASK] por género",
        height=max(400, n_rows * 200),
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor="#FAFAFA", paper_bgcolor="white",
        font=dict(family="Inter,sans-serif", size=11),
    )
    return fig


def _fig_semantic_search(results_list):
    """Tabla de resultados de búsqueda semántica."""
    rows = []
    for consulta, esperado, resultados in results_list:
        rows.append(html.Tr([
            html.Td(html.Strong(f'"{consulta[:55]}…"'),
                    colSpan=4,
                    style={"background": "#EDE7F6", "padding": "6px 10px",
                           "fontSize": "0.78rem", "color": "#4A148C"}),
        ]))
        rows.append(html.Tr([
            html.Td(f"→ Esperado: {esperado}",
                    colSpan=4,
                    style={"padding": "2px 10px 6px", "fontSize": "0.76rem", "color": "#888"}),
        ]))
        for _, row in resultados.iterrows():
            rows.append(html.Tr([
                html.Td(f"[{row['Genre']}]",
                        style={"fontFamily": "JetBrains Mono,monospace",
                               "fontSize": "0.76rem", "padding": "4px 10px",
                               "color": "#7B1FA2", "whiteSpace": "nowrap"}),
                html.Td(f"{row['Similitud']:.4f}",
                        style={"fontFamily": "JetBrains Mono,monospace",
                               "fontSize": "0.76rem", "padding": "4px 10px"}),
                html.Td(row["Song"],   style={"fontSize": "0.82rem", "padding": "4px 10px"}),
                html.Td(row["Artist"], style={"fontSize": "0.82rem", "padding": "4px 10px",
                                               "color": "#555"}),
            ]))
    return html.Table(
        [html.Thead(html.Tr([
            html.Th(h, style={"padding": "7px 10px", "fontSize": "0.8rem",
                               "color": "#6A1B9A", "borderBottom": "2px solid #D1A8E8"})
            for h in ("Género", "Similitud", "Canción", "Artista")
        ])),
         html.Tbody(rows)],
        style={"width": "100%", "borderCollapse": "collapse"},
    )


# ─── Layout ─────────────────────────────────────────────────────────────────
layout = html.Div([
    html.H2("Análisis Semántico con BERT"),
    html.P("Embeddings contextuales sobre letras musicales · Notebook 10",
           className="page-sub"),

    html.Div(className="info-box", children=[
        html.Strong("¿Por qué BERT y no BETO? "),
        "Las canciones del corpus están en inglés. BETO está entrenado en español; "
        "usarlo en inglés produce embeddings de baja calidad. Se usa ",
        html.Code("bert-base-uncased"), " (12 capas, 768d, ~110M parámetros). "
        "Primera carga: ~440 MB desde HuggingFace (cachéado localmente tras la primera vez).",
    ]),

    html.Div(className="card-panel", style={"marginBottom": "1rem"}, children=[
        html.P("Contenido", className="section-title"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "0.35rem",
                        "fontSize": "0.82rem", "color": "#4A148C"}, children=[
            html.Span("§1 · Arquitectura BERT (12 capas, 768d, ~110M params)"),
            html.Span("§2 · Polisemia contextual — misma palabra, distintos vectores"),
            html.Span("§3 · Búsqueda semántica de canciones por consulta"),
            html.Span("§4 · Masked Language Model (MLM) por género"),
            html.Span("§5 · Similitud entre géneros — centroides BERT [CLS]",
                      style={"gridColumn": "span 2"}),
        ]),
    ]),

    dbc.Row([
        dbc.Col(dbc.Button("▶  Cargar BERT y analizar", id="bert-btn",
                           style={"background": "linear-gradient(90deg,#880E4F,#E91E8C)",
                                  "border": "none", "fontFamily": "Inter,sans-serif",
                                  "fontWeight": "600", "borderRadius": "6px",
                                  "padding": "0.5rem 1.2rem"}),
                width="auto"),
        dbc.Col(dcc.Loading(html.Div(id="bert-status"), type="dot", color="#E91E8C"),
                width=True),
    ], align="center", className="mb-3"),

    html.Div(id="bert-results", style={"display": "none"}, children=[

        dbc.Row(id="bert-metrics", className="mb-3"),

        # Arquitectura BERT
        html.Div(className="card-panel", children=[
            html.P("§1 · Arquitectura bert-base-uncased", className="section-title"),
            dbc.Row([
                dbc.Col(html.Div(style={"display": "grid",
                                        "gridTemplateColumns": "1fr 1fr",
                                        "gap": "0.5rem", "fontSize": "0.84rem"}, children=[
                    html.Div([html.Span("Capas: ", style={"color": "#888"}),
                               html.Strong("12", style={"color": "#4A148C"})]),
                    html.Div([html.Span("Cabezas de atención: ", style={"color": "#888"}),
                               html.Strong("12", style={"color": "#4A148C"})]),
                    html.Div([html.Span("Dim. oculta: ", style={"color": "#888"}),
                               html.Strong("768", style={"color": "#4A148C"})]),
                    html.Div([html.Span("Parámetros: ", style={"color": "#888"}),
                               html.Strong("~110M", style={"color": "#4A148C"})]),
                    html.Div([html.Span("Dispositivo: ", style={"color": "#888"}),
                               html.Strong(id="bert-device", style={"color": "#4A148C"})]),
                    html.Div([html.Span("Representación: ", style={"color": "#888"}),
                               html.Strong("Token [CLS]", style={"color": "#4A148C"})]),
                ]), md=6),
                dbc.Col(html.Div(className="info-box", style={"marginBottom": "0"}, children=[
                    html.Strong("Diferencia vs Word2Vec: "),
                    "Word2Vec asigna un único vector por palabra, independiente del contexto. "
                    "BERT genera vectores distintos para la misma palabra según la oración — "
                    "capturando polisemia. «fire» en «on fire tonight» ≠ «open fire on the enemy».",
                ]), md=6),
            ]),
        ]),

        # Polisemia
        html.Div(className="card-panel", children=[
            html.P("§2 · Polisemia Contextual", className="section-title"),
            html.P("La misma palabra en contextos distintos produce vectores distintos. "
                   "Valores bajos en el heatmap = BERT distingue el significado.",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            html.Label("Palabra:", style={"fontSize": "0.82rem", "fontWeight": "600"}),
            dcc.Dropdown(id="bert-poly-drop",
                         options=[{"label": w, "value": w} for w in POLISEMIA],
                         value="fire", clearable=False,
                         style={"fontFamily": "JetBrains Mono,monospace",
                                "fontSize": "0.82rem", "maxWidth": "200px",
                                "marginBottom": "0.8rem"}),
            dcc.Graph(id="bert-poly-fig", config={"displayModeBar": False}),
            html.Div(id="bert-poly-stats",
                     style={"fontFamily": "JetBrains Mono,monospace",
                            "fontSize": "0.78rem", "color": "#666", "marginTop": "0.5rem"}),
        ]),

        # Búsqueda semántica
        html.Div(className="card-panel", children=[
            html.P("§3 · Búsqueda Semántica de Canciones", className="section-title"),
            html.P("Dado un texto de consulta, se encuentran las canciones más similares "
                   "usando distancia coseno entre embeddings BERT [CLS].",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            html.Div(id="bert-search-table"),
        ]),

        # MLM
        html.Div(className="card-panel", children=[
            html.P("§4 · Masked Language Model (MLM)", className="section-title"),
            html.P("BERT predice qué palabra va en [MASK] según el contexto del género.",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            dcc.Graph(id="bert-mlm-fig", config={"displayModeBar": False}),
        ]),

        # Similitud géneros
        html.Div(className="card-panel", children=[
            html.P("§5 · Similitud entre Géneros — Centroides BERT [CLS]",
                   className="section-title"),
            html.P("Al igual que con Word2Vec, los centroides BERT tienden a ser similares "
                   "entre géneros porque las letras comparten vocabulario base.",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            dcc.Graph(id="bert-heatmap-fig", config={"displayModeBar": False}),
        ]),
    ]),

    dcc.Store(id="bert-store"),
    dcc.Store(id="bert-poly-store"),
])


# ─── Callbacks ───────────────────────────────────────────────────────────────
@callback(
    Output("bert-status",       "children"),
    Output("bert-results",      "style"),
    Output("bert-metrics",      "children"),
    Output("bert-device",       "children"),
    Output("bert-mlm-fig",      "figure"),
    Output("bert-heatmap-fig",  "figure"),
    Output("bert-search-table", "children"),
    Output("bert-store",        "data"),
    Output("bert-poly-store",   "data"),
    Input("bert-btn", "n_clicks"),
    prevent_initial_call=True,
)
def load_bert(_):
    df, genres, err = _load_bert_data()
    if err:
        return (dbc.Alert(f"Error cargando datos: {err}", color="danger"),
                {"display": "none"}, [], "—", go.Figure(), go.Figure(), html.Div(), None, None)

    tokenizer, model, device, err2 = _load_bert_model()
    if err2:
        return (dbc.Alert(f"Error cargando BERT: {err2}", color="danger"),
                {"display": "none"}, [], "—", go.Figure(), go.Figure(), html.Div(), None, None)

    device_str = str(device)

    # ── Embeddings CLS por canción (muestra de 300 por velocidad) ────────
    from scipy.spatial.distance import cosine as sp_cos
    sample_df = df.groupby("Genre", group_keys=False).apply(
        lambda x: x.sample(min(30, len(x)), random_state=42)
    ).reset_index(drop=True)

    embs = np.array([_bert_cls_embedding(lyr, tokenizer, model, device)
                     for lyr in sample_df["Lyrics"].tolist()])

    # ── Centroides por género ─────────────────────────────────────────────
    centroides = {}
    for g in genres:
        idxs = sample_df[sample_df["Genre"] == g].index.tolist()
        pos  = [sample_df.index.get_loc(i) for i in idxs if i in sample_df.index]
        if pos:
            centroides[g] = embs[pos].mean(axis=0)

    # ── Polisemia (calcular para las 3 palabras) ──────────────────────────
    poly_embs = {}
    for palabra, contextos in POLISEMIA.items():
        resultados = []
        for genre, texto in contextos:
            emb = _embedding_en_contexto(texto, palabra, tokenizer, model, device)
            resultados.append({"genre": genre, "emb": emb.tolist()})
        poly_embs[palabra] = resultados

    # ── MLM ───────────────────────────────────────────────────────────────
    mlm_results = {}
    try:
        from transformers import pipeline as hf_pipeline
        import torch
        mlm_pipe = hf_pipeline("fill-mask", model="bert-base-uncased",
                                device=0 if torch.cuda.is_available() else -1)
        for genre, frase in MLM_FRASES.items():
            if genre not in genres:
                continue
            preds = mlm_pipe(frase, top_k=5)
            mlm_results[genre] = {
                "frase":  frase,
                "words":  [p["token_str"].strip() for p in preds],
                "probs":  [p["score"] for p in preds],
            }
    except Exception:
        pass  # MLM es opcional

    # ── Búsqueda semántica ────────────────────────────────────────────────
    search_results = []
    for consulta, esperado in CONSULTAS_SEMANTICAS:
        q_emb = _bert_cls_embedding(consulta, tokenizer, model, device)
        sims  = np.array([1 - sp_cos(q_emb, e) for e in embs])
        top   = np.argsort(sims)[::-1][:5]
        res   = sample_df.iloc[top].copy()
        res["Similitud"] = sims[top].round(4)
        search_results.append((consulta, esperado, res[["Song", "Artist", "Genre", "Similitud"]]))

    # ── Métricas ──────────────────────────────────────────────────────────
    metrics = dbc.Row([
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(f"{len(df):,}", className="metric-value"),
            html.Div("Canciones corpus", className="metric-label"),
        ]), md=3),
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(str(len(genres)), className="metric-value"),
            html.Div("Géneros", className="metric-label"),
        ]), md=3),
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div("768", className="metric-value"),
            html.Div("Dimensión BERT [CLS]", className="metric-label"),
        ]), md=3),
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(str(len(sample_df)), className="metric-value"),
            html.Div("Canciones analizadas", className="metric-label"),
        ]), md=3),
    ], className="mb-3")

    heatmap_fig = _fig_genre_heatmap_bert(centroides)
    mlm_fig     = _fig_mlm(mlm_results, genres) if mlm_results else go.Figure()
    search_div  = _fig_semantic_search(search_results)

    status = dbc.Alert(
        f"✓ BERT cargado en {device_str} — {len(sample_df)} canciones analizadas",
        color="success", className="mb-0 py-2",
        style={"fontFamily": "JetBrains Mono,monospace", "fontSize": "0.8rem"},
    )

    # Serializar poly_embs para el store
    store_poly = {w: [{"genre": r["genre"], "emb": r["emb"]} for r in rs]
                  for w, rs in poly_embs.items()}

    return (status, {"display": "block"}, metrics, device_str,
            mlm_fig, heatmap_fig, search_div,
            {"genres": genres}, store_poly)


@callback(
    Output("bert-poly-fig",   "figure"),
    Output("bert-poly-stats", "children"),
    Input("bert-poly-drop",   "value"),
    State("bert-poly-store",  "data"),
    prevent_initial_call=True,
)
def update_polisemia(palabra, store):
    if not palabra or not store or palabra not in store:
        return go.Figure(), ""
    resultados = [{"genre": r["genre"], "emb": np.array(r["emb"])}
                  for r in store[palabra]]
    figs = _fig_polisemia({palabra: resultados})
    fig  = figs[palabra]

    from scipy.spatial.distance import cosine as sp_cos
    sims = []
    for i in range(len(resultados)):
        for j in range(i + 1, len(resultados)):
            sims.append(1 - sp_cos(resultados[i]["emb"], resultados[j]["emb"]))
    stats = (f'sim_media={np.mean(sims):.4f}  |  '
             f'sim_min={np.min(sims):.4f}  |  '
             f'sim_max={np.max(sims):.4f}  '
             f'→ varianza mayor indica mejor captura de polisemia')
    return fig, stats


# -*- coding: utf-8 -*-
# pages/word2vec.py — Notebook 09: Análisis Semántico con Word2Vec
import re
import warnings
import numpy as np

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

warnings.filterwarnings("ignore")

dash.register_page(__name__, path="/word2vec", name="Word2Vec", title="Word2Vec – POS Tagging")

PALETTE = ["#4A148C", "#7B1FA2", "#AB47BC", "#E91E8C", "#CE93D8",
           "#7C4DFF", "#880E4F", "#4527A0", "#AD1457", "#6A1B9A"]

GRUPOS_TSNE = {
    "Emociones": ["love", "hate", "fear", "joy", "pain", "hope"],
    "Tiempo":    ["night", "day", "morning", "year", "time", "moment"],
    "Lugar":     ["road", "street", "home", "town", "city", "world"],
    "Acciones":  ["fight", "run", "dance", "sing", "fall", "rise"],
    "Identidad": ["heart", "soul", "mind", "body", "life", "blood"],
}
COLORES_GRUPOS = {
    "Emociones": "#E91E8C", "Tiempo": "#4A148C", "Lugar": "#2ecc71",
    "Acciones":  "#7B1FA2", "Identidad": "#AD1457",
}
PALABRAS_TEST = ["love", "fight", "night", "money", "soul", "fire", "road", "dark"]
ANALOGIAS = [
    (["love", "happy"],   ["sad"],     "love + happy − sad"),
    (["night", "dark"],   ["day"],     "night + dark − day"),
    (["king", "woman"],   ["man"],     "king − man + woman"),
    (["dance", "music"],  ["silence"], "dance + music − silence"),
    (["broken", "heart"], ["happy"],   "broken + heart − happy"),
]

PATRON_FRAGMENTO = re.compile(
    r"^(didn|couldn|wouldn|shouldn|won|don|isn|aren|wasn|weren|haven|hadn"
    r"|aint|wont|cant|gon|cause|ill|em|im|ur|ya|yer|ol|th|ve|re|ll|nd|nt)$"
)

# ─── helpers ────────────────────────────────────────────────────────────────

def _load_and_train():
    try:
        from data_cache import df_spacy
        from gensim.models import Word2Vec
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
            nlp = spacy.load("en_core_web_sm")
        STOP = nlp.Defaults.stop_words

        def clean(pos_tags):
            out = []
            for t in pos_tags:
                if not isinstance(t, (list, tuple)) or len(t) < 2:
                    continue
                tok, pos = str(t[0]).lower().strip(), t[1]
                if pos in ("PUNCT", "SPACE", "SYM", "NUM", "X", "PROPN"):
                    continue
                if len(tok) < 3 or tok in STOP:
                    continue
                if re.search(r"(.)\1{3,}", tok) or PATRON_FRAGMENTO.match(tok):
                    continue
                if re.search(r"\d", tok):
                    continue
                out.append(tok)
            return out

        df = df_spacy.copy()
        df["tokens_w2v"] = df["pos_tags_spacy"].apply(clean)
        conteo = df["Genre"].value_counts()
        genres = conteo[conteo >= 20].index.tolist()
        df = df[df["Genre"].isin(genres)].reset_index(drop=True)
        corpus = df["tokens_w2v"].tolist()
        model = Word2Vec(corpus, vector_size=100, window=5,
                         min_count=5, sg=1, epochs=20, seed=42, workers=2)
        return model, df, genres, None
    except Exception as e:
        return None, None, None, str(e)


def _centroides(model, df, genres):
    from scipy.spatial.distance import cosine as sp_cos
    c = {}
    for g in genres:
        toks = [t for ts in df[df["Genre"] == g]["tokens_w2v"] for t in ts if t in model.wv]
        if toks:
            c[g] = np.mean([model.wv[t] for t in toks], axis=0)
    return c


def _fig_neighbors(model, word):
    if word not in model.wv:
        return go.Figure().update_layout(title=f"'{word}' no está en el vocabulario")
    vecinos = model.wv.most_similar(word, topn=10)
    words, scores = zip(*vecinos)
    fig = go.Figure(go.Bar(
        x=list(scores), y=list(words), orientation="h",
        marker_color=PALETTE[3],
        text=[f"{s:.3f}" for s in scores], textposition="outside",
    ))
    fig.update_layout(
        title=f"Top 10 vecinos semánticos de «{word}» (Skip-Gram)",
        xaxis_title="Similitud coseno", yaxis=dict(autorange="reversed"),
        height=380, margin=dict(l=10, r=10, t=40, b=30),
        plot_bgcolor="#FAFAFA", paper_bgcolor="white",
        font=dict(family="Inter,sans-serif", size=12),
    )
    return fig


def _fig_heatmap(centroides):
    from scipy.spatial.distance import cosine as sp_cos
    ords = sorted(centroides)
    n = len(ords)
    mat = np.zeros((n, n))
    for i, g1 in enumerate(ords):
        for j, g2 in enumerate(ords):
            mat[i, j] = 1 - sp_cos(centroides[g1], centroides[g2])
    fig = go.Figure(go.Heatmap(
        z=mat, x=ords, y=ords, colorscale="RdPu",
        zmin=mat[~np.eye(n, dtype=bool)].min(), zmax=1.0,
        text=[[f"{mat[i,j]:.3f}" for j in range(n)] for i in range(n)],
        texttemplate="%{text}", textfont={"size": 10},
    ))
    fig.update_layout(
        title="Similitud coseno entre géneros (centroides Word2Vec Skip-Gram)",
        height=420, margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter,sans-serif", size=12),
        xaxis=dict(tickangle=-30),
    )
    return fig


def _fig_tsne(model):
    from sklearn.manifold import TSNE
    palabras_plot, vecs, cats = [], [], []
    for cat, words in GRUPOS_TSNE.items():
        for p in words:
            if p in model.wv:
                palabras_plot.append(p); vecs.append(model.wv[p]); cats.append(cat)
    if len(vecs) < 5:
        return go.Figure().update_layout(title="Pocas palabras disponibles para t-SNE")
    coords = TSNE(n_components=2, random_state=42,
                  perplexity=min(5, len(vecs) - 1)).fit_transform(np.array(vecs))
    traces = []
    for cat, color in COLORES_GRUPOS.items():
        idxs = [i for i, c in enumerate(cats) if c == cat]
        if not idxs:
            continue
        traces.append(go.Scatter(
            x=coords[idxs, 0], y=coords[idxs, 1], mode="markers+text",
            name=cat, marker=dict(color=color, size=10),
            text=[palabras_plot[i] for i in idxs],
            textposition="top center", textfont=dict(size=10),
        ))
    fig = go.Figure(data=traces)
    fig.update_layout(
        title="Proyección t-SNE de embeddings Word2Vec (grupos semánticos)",
        height=430, margin=dict(l=10, r=10, t=50, b=60),
        plot_bgcolor="#FAFAFA", paper_bgcolor="white",
        font=dict(family="Inter,sans-serif", size=12),
        legend=dict(orientation="h", y=-0.18),
    )
    return fig


def _fig_exclusive(model, centroides, genre):
    from scipy.spatial.distance import cosine as sp_cos
    if genre not in centroides:
        return go.Figure()
    c_obj   = centroides[genre]
    c_otros = [c for g, c in centroides.items() if g != genre]
    res = []
    for w in model.wv.index_to_key:
        v = model.wv[w]
        sim_obj   = 1 - sp_cos(v, c_obj)
        sim_otros = max(1 - sp_cos(v, c) for c in c_otros)
        m = sim_obj - sim_otros
        if m > 0:
            res.append((w, round(sim_obj, 4), round(m, 4)))
    res.sort(key=lambda x: -x[2])
    top = res[:12]
    words  = [r[0] for r in top]
    scores = [r[1] for r in top]
    color  = PALETTE[sorted(centroides).index(genre) % len(PALETTE)]
    fig = go.Figure(go.Bar(
        x=scores, y=words, orientation="h", marker_color=color,
        text=[f"{s:.3f}" for s in scores], textposition="outside",
    ))
    fig.update_layout(
        title=f"Vocabulario exclusivo — {genre}",
        xaxis_title="Similitud coseno al centroide",
        xaxis=dict(range=[0.3, 1.05]),
        yaxis=dict(autorange="reversed"),
        height=400, margin=dict(l=10, r=10, t=40, b=30),
        plot_bgcolor="#FAFAFA", paper_bgcolor="white",
        font=dict(family="Inter,sans-serif", size=12),
    )
    return fig


def _analogias_div(model):
    rows = []
    for pos, neg, desc in ANALOGIAS:
        ausentes = [w for w in pos + neg if w not in model.wv]
        if ausentes:
            resultado = f"⚠ fuera de vocab: {ausentes}"
            score     = "—"
        else:
            res = model.wv.most_similar(positive=pos, negative=neg,
                                        topn=len(pos) + len(neg) + 3)
            excl = set(pos + neg)
            res  = [(w, s) for w, s in res if w not in excl][:3]
            resultado = ", ".join(w for w, _ in res)
            score     = ", ".join(f"{s:.3f}" for _, s in res)
        rows.append(html.Tr([
            html.Td(desc,      style={"fontFamily": "JetBrains Mono,monospace",
                                      "fontSize": "0.78rem", "padding": "7px 12px"}),
            html.Td(resultado, style={"color": "#4A148C", "fontWeight": "600",
                                      "padding": "7px 12px", "fontSize": "0.82rem"}),
            html.Td(score,     style={"fontFamily": "JetBrains Mono,monospace",
                                      "fontSize": "0.78rem", "padding": "7px 12px",
                                      "color": "#888"}),
        ]))
    return html.Table([
        html.Thead(html.Tr([
            html.Th(h, style={"padding": "7px 12px", "fontSize": "0.8rem",
                               "color": "#6A1B9A", "borderBottom": "2px solid #D1A8E8"})
            for h in ("Analogía", "Resultado", "Score")
        ])),
        html.Tbody(rows),
    ], style={"width": "100%", "borderCollapse": "collapse", "fontSize": "0.82rem"})


# ─── Layout ─────────────────────────────────────────────────────────────────
layout = html.Div([
    html.H2("Análisis Semántico con Word2Vec"),
    html.P("Representaciones vectoriales estáticas sobre letras musicales · Notebook 09",
           className="page-sub"),

    html.Div(className="info-box", children=[
        html.Strong("¿Qué hace este análisis? "),
        "Entrena Word2Vec (Skip-Gram, 100d) sobre tokens limpios del corpus musical. "
        "Explora vecinos semánticos, analogías vectoriales, similitud entre géneros por centroides "
        "y vocabulario exclusivo de cada género. El entrenamiento tarda ~30–60 s dependiendo del corpus.",
    ]),

    html.Div(className="card-panel", style={"marginBottom": "1rem"}, children=[
        html.P("Contenido", className="section-title"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "0.35rem",
                        "fontSize": "0.82rem", "color": "#4A148C"}, children=[
            html.Span("§1 · Tokenización y limpieza desde POS tags"),
            html.Span("§2 · Entrenamiento Skip-Gram (100d, window=5)"),
            html.Span("§3 · Vecinos semánticos interactivos"),
            html.Span("§4 · Analogías vectoriales"),
            html.Span("§5 · Similitud coseno entre géneros (centroides)"),
            html.Span("§6 · Proyección t-SNE de grupos semánticos"),
            html.Span("§7 · Vocabulario exclusivo por género",
                      style={"gridColumn": "span 2"}),
        ]),
    ]),

    dbc.Row([
        dbc.Col(dbc.Button("▶  Cargar y entrenar Word2Vec", id="w2v-btn",
                           style={"background": "linear-gradient(90deg,#4A148C,#7B1FA2)",
                                  "border": "none", "fontFamily": "Inter,sans-serif",
                                  "fontWeight": "600", "borderRadius": "6px", "padding": "0.5rem 1.2rem"}),
                width="auto"),
        dbc.Col(dcc.Loading(html.Div(id="w2v-status"), type="dot", color="#7B1FA2"), width=True),
    ], align="center", className="mb-3"),

    html.Div(id="w2v-results", style={"display": "none"}, children=[

        dbc.Row(id="w2v-metrics", className="mb-3"),

        html.Div(className="card-panel", children=[
            html.P("§3 · Vecinos Semánticos (Skip-Gram)", className="section-title"),
            html.P("Las palabras más cercanas en el espacio vectorial deben ser "
                   "semánticamente coherentes — verificación cualitativa del modelo.",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            dbc.Row([
                dbc.Col([
                    html.Label("Palabra objetivo:", style={"fontSize": "0.82rem", "fontWeight": "600"}),
                    dcc.Dropdown(id="w2v-word-drop", options=[], value=None, clearable=False,
                                 style={"fontFamily": "JetBrains Mono,monospace", "fontSize": "0.82rem"}),
                ], md=3),
                dbc.Col(dcc.Graph(id="w2v-neighbors-fig", config={"displayModeBar": False}), md=9),
            ]),
        ]),

        html.Div(className="card-panel", children=[
            html.P("§4 · Analogías Vectoriales", className="section-title"),
            html.P(["Propiedad clave de Word2Vec: las relaciones semánticas se codifican como ",
                    html.Strong("direcciones"), " en el espacio vectorial."],
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            html.Div(id="w2v-analogias"),
        ]),

        html.Div(className="card-panel", children=[
            html.P("§5 · Similitud entre Géneros (Centroides)", className="section-title"),
            html.P("Similitudes altas (> 0.90) son esperables — las letras comparten vocabulario base.",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            dcc.Graph(id="w2v-heatmap-fig", config={"displayModeBar": False}),
        ]),

        html.Div(className="card-panel", children=[
            html.P("§6 · Proyección t-SNE de Embeddings", className="section-title"),
            html.P("Palabras del mismo grupo semántico deberían aparecer cercanas.",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            dcc.Graph(id="w2v-tsne-fig", config={"displayModeBar": False}),
        ]),

        html.Div(className="card-panel", children=[
            html.P("§7 · Vocabulario Exclusivo por Género", className="section-title"),
            html.P("Palabras cuyo vector queda más cerca del centroide de un género que de todos los demás.",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            dbc.Row([
                dbc.Col([
                    html.Label("Género:", style={"fontSize": "0.82rem", "fontWeight": "600"}),
                    dcc.Dropdown(id="w2v-genre-drop", options=[], value=None, clearable=False,
                                 style={"fontFamily": "Inter,sans-serif", "fontSize": "0.82rem"}),
                ], md=3),
                dbc.Col(dcc.Graph(id="w2v-exclusive-fig", config={"displayModeBar": False}), md=9),
            ]),
        ]),
    ]),

    dcc.Store(id="w2v-store"),
])


# ─── Callbacks ───────────────────────────────────────────────────────────────
@callback(
    Output("w2v-status",       "children"),
    Output("w2v-results",      "style"),
    Output("w2v-metrics",      "children"),
    Output("w2v-word-drop",    "options"),
    Output("w2v-word-drop",    "value"),
    Output("w2v-genre-drop",   "options"),
    Output("w2v-genre-drop",   "value"),
    Output("w2v-heatmap-fig",  "figure"),
    Output("w2v-tsne-fig",     "figure"),
    Output("w2v-analogias",    "children"),
    Output("w2v-store",        "data"),
    Input("w2v-btn", "n_clicks"),
    prevent_initial_call=True,
)
def load_w2v(_):
    model, df, genres, err = _load_and_train()
    if err:
        return (dbc.Alert(f"Error: {err}", color="danger"),
                {"display": "none"}, [], [], None, [], None,
                go.Figure(), go.Figure(), html.Div(), None)

    total_toks = sum(len(t) for t in df["tokens_w2v"])
    vocab_size = len(model.wv)
    cents      = _centroides(model, df, genres)

    metrics = dbc.Row([
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(f"{len(df):,}", className="metric-value"),
            html.Div("Canciones", className="metric-label"),
        ]), md=3),
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(str(len(genres)), className="metric-value"),
            html.Div("Géneros", className="metric-label"),
        ]), md=3),
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(f"{vocab_size:,}", className="metric-value"),
            html.Div("Vocabulario Skip-Gram", className="metric-label"),
        ]), md=3),
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(f"{total_toks:,}", className="metric-value"),
            html.Div("Tokens totales", className="metric-label"),
        ]), md=3),
    ], className="mb-3")

    word_opts  = [{"label": w, "value": w} for w in PALABRAS_TEST if w in model.wv]
    genre_opts = [{"label": g, "value": g} for g in sorted(genres)]

    status = dbc.Alert(
        f"✓ Modelo entrenado — {vocab_size:,} palabras | {len(genres)} géneros",
        color="success", className="mb-0 py-2",
        style={"fontFamily": "JetBrains Mono,monospace", "fontSize": "0.8rem"},
    )
    return (
        status, {"display": "block"}, metrics,
        word_opts, word_opts[0]["value"] if word_opts else None,
        genre_opts, genre_opts[0]["value"] if genre_opts else None,
        _fig_heatmap(cents), _fig_tsne(model), _analogias_div(model),
        {"genres": genres},
    )


@callback(
    Output("w2v-neighbors-fig", "figure"),
    Input("w2v-word-drop", "value"),
    State("w2v-store", "data"),
    prevent_initial_call=True,
)
def update_neighbors(word, store):
    if not word or not store:
        return go.Figure()
    model, *_ = _load_and_train()
    return _fig_neighbors(model, word) if model else go.Figure()


@callback(
    Output("w2v-exclusive-fig", "figure"),
    Input("w2v-genre-drop", "value"),
    State("w2v-store", "data"),
    prevent_initial_call=True,
)
def update_exclusive(genre, store):
    if not genre or not store:
        return go.Figure()
    model, df, genres, err = _load_and_train()
    if err or model is None:
        return go.Figure()
    cents = _centroides(model, df, genres)
    return _fig_exclusive(model, cents, genre)


# -*- coding: utf-8 -*-
# pages/comparacion.py — Notebook 11: Comparación Final TF-IDF vs Word2Vec vs BERT
import warnings
import numpy as np
import re

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

dash.register_page(__name__, path="/comparacion", name="Comparación",
                   title="Comparación – POS Tagging")

PALETTE = ["#4A148C", "#E91E8C", "#AB47BC", "#CE93D8",
           "#7C4DFF", "#880E4F", "#4527A0", "#AD1457", "#6A1B9A", "#7B1FA2"]

PATRON_FRAGMENTO = re.compile(
    r"^(didn|couldn|wouldn|shouldn|won|don|isn|aren|wasn|weren|haven|hadn"
    r"|aint|wont|cant|gon|cause|ill|em|im|ur|ya|yer|ol|th|ve|re|ll|nd|nt)$"
)

# ─── helpers ────────────────────────────────────────────────────────────────

def _load_everything():
    """Carga datos, entrena W2V, carga BERT y construye las tres matrices."""
    try:
        from data_cache import df_clean, df_spacy
        import spacy, torch
        from gensim.models import Word2Vec
        from transformers import AutoTokenizer, AutoModel
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import LabelEncoder

        # ── corpus ───────────────────────────────────────────────────────
        df = df_clean[["Song", "Artist", "Genre", "Song year", "Lyrics"]].copy()
        df = df.dropna(subset=["Lyrics", "Genre"])
        df["Lyrics"] = df["Lyrics"].astype(str).str.strip()
        df = df[df["Lyrics"].str.len() > 50].reset_index(drop=True)

        conteo = df["Genre"].value_counts()
        genres = conteo[conteo >= 20].index.tolist()
        df = df[df["Genre"].isin(genres)].reset_index(drop=True)

        # ── TF-IDF ───────────────────────────────────────────────────────
        tfidf_vec = TfidfVectorizer(max_features=5000, stop_words="english",
                                    min_df=2, sublinear_tf=True)
        X_tfidf = tfidf_vec.fit_transform(df["Lyrics"].tolist()).toarray()

        # ── Word2Vec ──────────────────────────────────────────────────────
        try:
            nlp  = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
            nlp = spacy.load("en_core_web_sm")
        STOP = nlp.Defaults.stop_words

        spacy_df = df_spacy.copy()
        spacy_df = spacy_df[spacy_df["Genre"].isin(genres)].reset_index(drop=True)

        def clean(pos_tags):
            out = []
            for t in pos_tags:
                if not isinstance(t, (list, tuple)) or len(t) < 2:
                    continue
                tok, pos = str(t[0]).lower().strip(), t[1]
                if pos in ("PUNCT", "SPACE", "SYM", "NUM", "X", "PROPN"):
                    continue
                if len(tok) < 3 or tok in STOP:
                    continue
                if re.search(r"(.)\1{3,}", tok) or PATRON_FRAGMENTO.match(tok):
                    continue
                if re.search(r"\d", tok):
                    continue
                out.append(tok)
            return out

        spacy_df["tokens_w2v"] = spacy_df["pos_tags_spacy"].apply(clean)
        corpus = spacy_df["tokens_w2v"].tolist()
        w2v_model = Word2Vec(corpus, vector_size=100, window=5,
                             min_count=5, sg=1, epochs=20, seed=42, workers=2)

        # Embeddings W2V por canción (promedio de tokens)
        def w2v_avg(tokens):
            vecs = [w2v_model.wv[t] for t in tokens if t in w2v_model.wv]
            return np.mean(vecs, axis=0) if vecs else np.zeros(100)

        # Alinear df y spacy_df por Song
        merged = df.merge(spacy_df[["Song", "tokens_w2v"]], on="Song", how="left")
        merged["tokens_w2v"] = merged["tokens_w2v"].apply(
            lambda x: x if isinstance(x, list) else []
        )
        X_w2v = np.array([w2v_avg(t) for t in merged["tokens_w2v"].tolist()])

        # ── BERT [CLS] ────────────────────────────────────────────────────
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        bert_model = AutoModel.from_pretrained("bert-base-uncased").to(device)
        bert_model.eval()

        def bert_cls(text):
            inputs = tokenizer(text, return_tensors="pt",
                               truncation=True, max_length=128).to(device)
            with torch.no_grad():
                out = bert_model(**inputs)
            return out.last_hidden_state[0, 0].cpu().numpy()

        # Muestra estratificada para mantener velocidad razonable
        MUESTRA = 40
        sample_df = df.groupby("Genre", group_keys=False).apply(
            lambda x: x.sample(min(MUESTRA, len(x)), random_state=42)
        ).reset_index(drop=True)

        X_tfidf_s = X_tfidf[sample_df.index]
        X_w2v_s   = X_w2v[sample_df.index]
        X_bert_s  = np.array([bert_cls(lyr) for lyr in sample_df["Lyrics"].tolist()])

        le = _make_le(genres)
        labels = le.transform(sample_df["Genre"].tolist())

        return (sample_df, genres, le, labels,
                X_tfidf_s, X_w2v_s, X_bert_s,
                X_tfidf, X_w2v, None)
    except Exception as e:
        return (None,) * 9 + (str(e),)


def _make_le(genres):
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    le.fit(sorted(genres))
    return le


def _run_classification(X_tfidf, X_w2v, X_bert, labels, genres):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import classification_report
    from sklearn.preprocessing import LabelEncoder

    le = _make_le(genres)
    REPS = {"TF-IDF (BoW)": X_tfidf, "Word2Vec": X_w2v, "BERT [CLS]": X_bert}
    clf_scores, clf_std, clf_reports = {}, {}, {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for nombre, X in REPS.items():
        scaler = StandardScaler()
        X_sc   = scaler.fit_transform(X)
        clf_cv = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
        scores = cross_val_score(clf_cv, X_sc, labels, cv=cv, scoring="accuracy")
        clf_scores[nombre] = float(scores.mean())
        clf_std[nombre]    = float(scores.std())

        X_tr, X_te, y_tr, y_te = train_test_split(
            X_sc, labels, test_size=0.25, random_state=42, stratify=labels)
        clf_rep = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
        clf_rep.fit(X_tr, y_tr)
        clf_reports[nombre] = classification_report(
            y_te, clf_rep.predict(X_te),
            target_names=le.classes_, output_dict=True)

    return clf_scores, clf_std, clf_reports


def _run_clustering(X_tfidf, X_w2v, X_bert, labels, n_clusters):
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    REPS = {"TF-IDF (BoW)": X_tfidf, "Word2Vec": X_w2v, "BERT [CLS]": X_bert}
    sil_scores = {}
    for nombre, X in REPS.items():
        scaler = StandardScaler()
        X_sc   = scaler.fit_transform(X)
        n_pca  = min(50, X_sc.shape[1])
        pca    = PCA(n_components=n_pca, random_state=42)
        X_pca  = pca.fit_transform(X_sc)
        km     = KMeans(n_clusters=n_clusters, random_state=42, n_init=15)
        lab    = km.fit_predict(X_pca)
        sil    = silhouette_score(X_pca, lab, sample_size=min(2000, len(X_pca)))
        sil_scores[nombre] = float(sil)
    return sil_scores


def _run_tsne(X_tfidf, X_w2v, X_bert):
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    REPS = {"TF-IDF (BoW)": X_tfidf, "Word2Vec": X_w2v, "BERT [CLS]": X_bert}
    tsne_res = {}
    for nombre, X in REPS.items():
        X_sc  = StandardScaler().fit_transform(X)
        n_pca = min(30, X_sc.shape[1])
        X_pca = PCA(n_components=n_pca, random_state=42).fit_transform(X_sc)
        coords = TSNE(n_components=2, random_state=42,
                      perplexity=min(20, len(X_pca) // 4),
                      n_iter=800).fit_transform(X_pca)
        tsne_res[nombre] = coords
    return tsne_res


# ─── figuras ────────────────────────────────────────────────────────────────

def _fig_comparison_bars(clf_scores, clf_std, sil_scores):
    nombres = list(clf_scores.keys())
    colors  = [PALETTE[0], PALETTE[1], PALETTE[2]]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Clasificación de Género (CV 5-fold, Accuracy)",
                                        f"Clustering K-Means (Silhouette Score)"])

    fig.add_trace(go.Bar(
        x=nombres, y=[clf_scores[n] for n in nombres],
        error_y=dict(type="data", array=[clf_std[n] for n in nombres]),
        marker_color=colors, name="Accuracy",
        text=[f"{clf_scores[n]:.3f}" for n in nombres],
        textposition="outside", showlegend=False,
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=nombres, y=[sil_scores[n] for n in nombres],
        marker_color=colors, name="Silhouette",
        text=[f"{sil_scores[n]:.4f}" for n in nombres],
        textposition="outside", showlegend=False,
    ), row=1, col=2)

    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=60, b=40),
        plot_bgcolor="#FAFAFA", paper_bgcolor="white",
        font=dict(family="Inter,sans-serif", size=12),
    )
    fig.update_yaxes(title_text="Accuracy", row=1, col=1)
    fig.update_yaxes(title_text="Silhouette Score", row=1, col=2)
    return fig


def _fig_tsne_compare(tsne_res, sample_df, genres):
    import pandas as pd
    genres_uniq = sorted(set(sample_df["Genre"].tolist()))
    color_dict  = {g: PALETTE[i % len(PALETTE)] for i, g in enumerate(genres_uniq)}
    nombres = list(tsne_res.keys())
    fig = make_subplots(rows=1, cols=3, subplot_titles=nombres,
                        horizontal_spacing=0.06)
    shown = set()
    for col_idx, (nombre, coords) in enumerate(tsne_res.items(), 1):
        for genre in genres_uniq:
            mask = [g == genre for g in sample_df["Genre"].tolist()]
            xs = coords[mask, 0]
            ys = coords[mask, 1]
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="markers",
                name=genre,
                marker=dict(color=color_dict[genre], size=7, opacity=0.75),
                showlegend=(genre not in shown and col_idx == 3),
                legendgroup=genre,
            ), row=1, col=col_idx)
            shown.add(genre)
    fig.update_layout(
        title=f"t-SNE — Separación entre géneros por representación ({len(sample_df)} canciones)",
        height=420, margin=dict(l=10, r=10, t=70, b=60),
        plot_bgcolor="#FAFAFA", paper_bgcolor="white",
        font=dict(family="Inter,sans-serif", size=11),
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
    )
    return fig


def _fig_f1_heatmap(clf_reports, genres):
    from sklearn.preprocessing import LabelEncoder
    le = _make_le(genres)
    nombres = list(clf_reports.keys())
    f1_mat  = np.array([
        [clf_reports[n].get(g, {}).get("f1-score", 0) for g in le.classes_]
        for n in nombres
    ])
    fig = go.Figure(go.Heatmap(
        z=f1_mat, x=list(le.classes_), y=nombres,
        colorscale="RdYlGn", zmin=0, zmax=1,
        text=[[f"{v:.3f}" for v in row] for row in f1_mat],
        texttemplate="%{text}", textfont={"size": 11},
    ))
    fig.update_layout(
        title="F1-Score por representación y género<br>"
              "<sup>Verde = bien clasificado | Rojo = difícil de clasificar</sup>",
        height=260, margin=dict(l=10, r=10, t=70, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter,sans-serif", size=11),
        xaxis=dict(tickangle=-30),
    )
    return fig


def _dispersion_table(X_tfidf, X_w2v, X_bert):
    datos = [
        ("TF-IDF (BoW)", X_tfidf.shape, f"{(X_tfidf == 0).mean()*100:.1f}%",
         "Alta dim. dispersa — no captura semántica entre palabras distintas"),
        ("Word2Vec",     X_w2v.shape,   f"{(X_w2v == 0).mean()*100:.1f}%",
         "Densa, estática — un vector por palabra independiente del contexto"),
        ("BERT [CLS]",   X_bert.shape,  f"{(X_bert == 0).mean()*100:.1f}%",
         "Densa, contextual — captura polisemia y semántica global"),
    ]
    rows = [
        html.Tr([
            html.Td(nombre, style={"fontFamily": "JetBrains Mono,monospace",
                                   "fontSize": "0.82rem", "padding": "7px 12px",
                                   "fontWeight": "600", "color": PALETTE[i]}),
            html.Td(str(shape), style={"fontFamily": "JetBrains Mono,monospace",
                                        "fontSize": "0.78rem", "padding": "7px 12px"}),
            html.Td(disp,  style={"fontFamily": "JetBrains Mono,monospace",
                                   "fontSize": "0.82rem", "padding": "7px 12px",
                                   "textAlign": "center"}),
            html.Td(desc, style={"fontSize": "0.8rem", "padding": "7px 12px", "color": "#555"}),
        ]) for i, (nombre, shape, disp, desc) in enumerate(datos)
    ]
    return html.Table([
        html.Thead(html.Tr([
            html.Th(h, style={"padding": "7px 12px", "fontSize": "0.8rem",
                               "color": "#6A1B9A", "borderBottom": "2px solid #D1A8E8"})
            for h in ("Representación", "Shape", "Dispersión", "Característica clave")
        ])),
        html.Tbody(rows),
    ], style={"width": "100%", "borderCollapse": "collapse"})


def _resumen_div(clf_scores, clf_std, sil_scores, genres):
    mejor_clf = max(clf_scores, key=clf_scores.get)
    mejor_sil = max(sil_scores, key=sil_scores.get)

    def row(nombre, acc, std, sil):
        star_c = "🏆 " if nombre == mejor_clf else "   "
        star_s = "🏆 " if nombre == mejor_sil else "   "
        return html.Tr([
            html.Td(nombre, style={"fontFamily": "JetBrains Mono,monospace",
                                   "fontWeight": "600", "padding": "7px 12px",
                                   "fontSize": "0.82rem"}),
            html.Td(f"{star_c}acc = {acc:.4f} ± {std:.4f}",
                    style={"fontFamily": "JetBrains Mono,monospace",
                           "fontSize": "0.82rem", "padding": "7px 12px"}),
            html.Td(f"{star_s}sil = {sil:.4f}",
                    style={"fontFamily": "JetBrains Mono,monospace",
                           "fontSize": "0.82rem", "padding": "7px 12px"}),
        ])

    table = html.Table([
        html.Thead(html.Tr([
            html.Th(h, style={"padding": "7px 12px", "fontSize": "0.8rem",
                               "color": "#6A1B9A", "borderBottom": "2px solid #D1A8E8"})
            for h in ("Representación", "Clasificación (LR, CV 5-fold)", "Clustering (Silhouette)")
        ])),
        html.Tbody([row(n, clf_scores[n], clf_std[n], sil_scores[n])
                    for n in clf_scores]),
    ], style={"width": "100%", "borderCollapse": "collapse", "marginBottom": "1rem"})

    conclusiones = html.Div([
        html.P("Conclusión general:", style={"fontWeight": "700", "color": "#4A148C",
                                              "marginBottom": "0.5rem"}),
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr",
                        "gap": "0.8rem"}, children=[
            html.Div(style={"background": "#EDE7F6", "borderRadius": "8px",
                            "padding": "0.9rem", "borderLeft": f"4px solid {PALETTE[0]}"}, children=[
                html.Strong("TF-IDF (BoW)", style={"color": PALETTE[0]}),
                html.Ul([
                    html.Li("Alta dimensionalidad (5000 features)"),
                    html.Li("Muy dispersa (~99%)"),
                    html.Li("No captura semántica entre palabras distintas"),
                    html.Li("Fuerte en clasificación por especificidad léxica"),
                ], style={"fontSize": "0.78rem", "paddingLeft": "1.2rem",
                          "marginTop": "0.4rem", "color": "#444"}),
            ]),
            html.Div(style={"background": "#EDE7F6", "borderRadius": "8px",
                            "padding": "0.9rem", "borderLeft": f"4px solid {PALETTE[1]}"}, children=[
                html.Strong("Word2Vec", style={"color": PALETTE[1]}),
                html.Ul([
                    html.Li("Vectores densos (100d), estáticos por palabra"),
                    html.Li("Captura analogías y vecinos semánticos"),
                    html.Li("Un único vector por palabra, sin contexto"),
                    html.Li("Bueno para análisis de vocabulario por género"),
                ], style={"fontSize": "0.78rem", "paddingLeft": "1.2rem",
                          "marginTop": "0.4rem", "color": "#444"}),
            ]),
            html.Div(style={"background": "#EDE7F6", "borderRadius": "8px",
                            "padding": "0.9rem", "borderLeft": f"4px solid {PALETTE[2]}"}, children=[
                html.Strong("BERT [CLS]", style={"color": PALETTE[2]}),
                html.Ul([
                    html.Li("Vectores densos (768d), contextuales"),
                    html.Li("Captura polisemia — mismo token, distinto vector"),
                    html.Li("Mejor para búsqueda semántica"),
                    html.Li("Más costoso computacionalmente"),
                ], style={"fontSize": "0.78rem", "paddingLeft": "1.2rem",
                          "marginTop": "0.4rem", "color": "#444"}),
            ]),
        ]),
    ])
    return html.Div([table, conclusiones])


# ─── Layout ─────────────────────────────────────────────────────────────────
layout = html.Div([
    html.H2("Comparación Final de Representaciones"),
    html.P("TF-IDF (BoW) · Word2Vec · BERT [CLS] · Notebook 11",
           className="page-sub"),

    html.Div(className="info-box", children=[
        html.Strong("¿Qué compara este análisis? "),
        "Evalúa las tres representaciones vectoriales sobre el mismo corpus usando: "
        "Clasificación de género (Regresión Logística, CV 5-fold), "
        "Clustering K-Means + Silhouette Score, "
        "Proyección t-SNE y F1-Score detallado por género. "
        "Este módulo entrena Word2Vec y carga BERT en el servidor — puede tardar 2-5 minutos.",
    ]),

    html.Div(className="card-panel", style={"marginBottom": "1rem"}, children=[
        html.P("Contenido", className="section-title"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "0.35rem",
                        "fontSize": "0.82rem", "color": "#4A148C"}, children=[
            html.Span("§1 · Matrices de representación (shape, dispersión)"),
            html.Span("§2 · Clasificación LR — Accuracy CV 5-fold"),
            html.Span("§3 · Clustering K-Means — Silhouette Score"),
            html.Span("§4 · Visualización t-SNE comparativa (3 paneles)"),
            html.Span("§5 · F1-Score detallado por representación y género"),
            html.Span("§6 · Resumen y conclusiones"),
        ]),
    ]),

    dbc.Row([
        dbc.Col(dbc.Button("▶  Ejecutar comparación completa", id="cmp-btn",
                           style={"background": "linear-gradient(90deg,#4527A0,#7C4DFF)",
                                  "border": "none", "fontFamily": "Inter,sans-serif",
                                  "fontWeight": "600", "borderRadius": "6px",
                                  "padding": "0.5rem 1.2rem"}),
                width="auto"),
        dbc.Col(dcc.Loading(html.Div(id="cmp-status"), type="dot", color="#7C4DFF"),
                width=True),
    ], align="center", className="mb-3"),

    html.Div(id="cmp-results", style={"display": "none"}, children=[

        dbc.Row(id="cmp-metrics", className="mb-3"),

        # Matrices
        html.Div(className="card-panel", children=[
            html.P("§1 · Matrices de Representación", className="section-title"),
            html.Div(id="cmp-disp-table"),
        ]),

        # Clasificación + Clustering
        html.Div(className="card-panel", children=[
            html.P("§2 · Clasificación y §3 · Clustering — Comparativa", className="section-title"),
            dcc.Graph(id="cmp-bars-fig", config={"displayModeBar": False}),
        ]),

        # t-SNE
        html.Div(className="card-panel", children=[
            html.P("§4 · Proyección t-SNE — Las tres representaciones",
                   className="section-title"),
            html.P("¿Qué representación separa mejor los géneros en 2D?",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            dcc.Graph(id="cmp-tsne-fig", config={"displayModeBar": False}),
        ]),

        # F1 heatmap
        html.Div(className="card-panel", children=[
            html.P("§5 · F1-Score por Representación y Género",
                   className="section-title"),
            html.P("Qué géneros son más fáciles/difíciles de clasificar con cada representación.",
                   style={"fontSize": "0.82rem", "color": "#555", "marginBottom": "0.8rem"}),
            dcc.Graph(id="cmp-f1-fig", config={"displayModeBar": False}),
        ]),

        # Resumen
        html.Div(className="card-panel", children=[
            html.P("§6 · Resumen y Conclusiones", className="section-title"),
            html.Div(id="cmp-summary"),
        ]),
    ]),

    dcc.Store(id="cmp-store"),
])


# ─── Callbacks ───────────────────────────────────────────────────────────────
@callback(
    Output("cmp-status",     "children"),
    Output("cmp-results",    "style"),
    Output("cmp-metrics",    "children"),
    Output("cmp-disp-table", "children"),
    Output("cmp-bars-fig",   "figure"),
    Output("cmp-tsne-fig",   "figure"),
    Output("cmp-f1-fig",     "figure"),
    Output("cmp-summary",    "children"),
    Output("cmp-store",      "data"),
    Input("cmp-btn", "n_clicks"),
    prevent_initial_call=True,
)
def run_comparison(_):
    result = _load_everything()
    (sample_df, genres, le, labels,
     X_tfidf_s, X_w2v_s, X_bert_s,
     X_tfidf_full, X_w2v_full, err) = result

    if err:
        return (dbc.Alert(f"Error: {err}", color="danger"),
                {"display": "none"}, [], html.Div(),
                go.Figure(), go.Figure(), go.Figure(), html.Div(), None)

    clf_scores, clf_std, clf_reports = _run_classification(
        X_tfidf_s, X_w2v_s, X_bert_s, labels, genres)
    sil_scores = _run_clustering(X_tfidf_s, X_w2v_s, X_bert_s, labels, len(genres))
    tsne_res   = _run_tsne(X_tfidf_s, X_w2v_s, X_bert_s)

    mejor_clf = max(clf_scores, key=clf_scores.get)
    mejor_sil = max(sil_scores, key=sil_scores.get)

    metrics = dbc.Row([
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(str(len(sample_df)), className="metric-value"),
            html.Div("Canciones analizadas", className="metric-label"),
        ]), md=3),
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(str(len(genres)), className="metric-value"),
            html.Div("Géneros", className="metric-label"),
        ]), md=3),
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(f"{clf_scores[mejor_clf]:.3f}", className="metric-value"),
            html.Div(f"Mejor Accuracy ({mejor_clf})", className="metric-label"),
        ]), md=3),
        dbc.Col(html.Div(className="metric-card", children=[
            html.Div(f"{sil_scores[mejor_sil]:.4f}", className="metric-value"),
            html.Div(f"Mejor Silhouette ({mejor_sil})", className="metric-label"),
        ]), md=3),
    ], className="mb-3")

    bars_fig = _fig_comparison_bars(clf_scores, clf_std, sil_scores)
    tsne_fig = _fig_tsne_compare(tsne_res, sample_df, genres)
    f1_fig   = _fig_f1_heatmap(clf_reports, genres)
    disp_tab = _dispersion_table(X_tfidf_s, X_w2v_s, X_bert_s)
    summary  = _resumen_div(clf_scores, clf_std, sil_scores, genres)

    status = dbc.Alert(
        f"✓ Análisis completo — {len(sample_df)} canciones | "
        f"Mejor clasificación: {mejor_clf} ({clf_scores[mejor_clf]:.3f}) | "
        f"Mejor clustering: {mejor_sil} ({sil_scores[mejor_sil]:.4f})",
        color="success", className="mb-0 py-2",
        style={"fontFamily": "JetBrains Mono,monospace", "fontSize": "0.78rem"},
    )

    store = {"clf_scores": clf_scores, "sil_scores": sil_scores, "genres": genres}

    return (status, {"display": "block"}, metrics, disp_tab,
            bars_fig, tsne_fig, f1_fig, summary, store)

