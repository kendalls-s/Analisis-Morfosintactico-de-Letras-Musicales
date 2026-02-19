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
