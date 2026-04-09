import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Inicialización de la App
app = Dash(
    __name__,
    use_pages=True, # Habilita multi-páginas (requiere carpeta /pages)
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800"
        "&family=DM+Mono:wght@400;500&display=swap",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "Análisis Semántico · Letras Musicales"
server = app.server

# Configuración de Navegación
NAV_ITEMS = [
    {"label": "◈  Resumen General",   "href": "/"},
    {"label": "⬡  Word2Vec",          "href": "/word2vec"},
    {"label": "◉  BERT",              "href": "/bert"},
    {"label": "⊞  Comparación Final", "href": "/comparacion"},
    {"label": "≋  Corpus & MongoDB",  "href": "/corpus"},
]

# Títulos dinámicos para la barra superior
PAGE_TITLES = {
    "/":            "Resumen General",
    "/word2vec":    "Word2Vec — Representaciones Estáticas",
    "/bert":        "BERT — Embeddings Contextuales",
    "/comparacion": "Comparación Final · TF-IDF vs Word2Vec vs BERT",
    "/corpus":      "Corpus & Pipeline MongoDB",
}

# Componente Sidebar
sidebar = html.Aside(id="sidebar", className="sidebar", children=[
    html.Div(className="sidebar-logo", children=[
        html.Span("♪", className="logo-icon"),
        html.Div([
            html.Div("SemanticLyrics", className="logo-title"),
            html.Div("Proyecto 2 · CUC", className="logo-sub"),
        ]),
    ]),
    html.Nav(className="sidebar-nav", children=[
        dcc.Link(item["label"], href=item["href"],
                 className="nav-item", id=f"nav-{i}")
        for i, item in enumerate(NAV_ITEMS)
    ]),
    html.Div(className="sidebar-footer", children=[
        html.Span("Word2Vec", className="badge-pill"),
        html.Span("BERT",     className="badge-pill"),
        html.Span("MongoDB",  className="badge-pill"),
    ]),
])

# Componente Barra Superior
topbar = html.Header(className="topbar", children=[
    html.Div(id="page-title", className="topbar-title", children="Resumen General"),
    html.Div(className="topbar-meta", children=[
        html.Span("Minería de Textos",   className="meta-chip"),
        html.Span("Análisis Semántico",  className="meta-chip accent"),
    ]),
])

# Layout Principal
app.layout = html.Div(className="app-wrapper", children=[
    dcc.Location(id="url", refresh=False),
    sidebar,
    html.Main(className="main-content", children=[
        topbar,
        html.Div(id="page-content", className="page-container",
                 children=dash.page_container),
    ]),
])

# --- CALLBACKS GLOBALES ---

# 1. Resaltar item activo en el menú
@app.callback(
    [Output(f"nav-{i}", "className") for i in range(len(NAV_ITEMS))],
    Input("url", "pathname"),
)
def highlight_nav(pathname):
    return [
        "nav-item active" if (pathname == item["href"]) or
        (item["href"] != "/" and pathname.startswith(item["href"]))
        else "nav-item"
        for item in NAV_ITEMS
    ]

# 2. Actualizar título de la página
@app.callback(Output("page-title", "children"), Input("url", "pathname"))
def update_title(pathname):
    return PAGE_TITLES.get(pathname, "Análisis Semántico")

# --- EJECUCIÓN DEL SERVIDOR ---
if __name__ == "__main__":
    # IMPORTANTE: use_reloader=False evita el error OSError: [WinError 10038] en Windows
    app.run(debug=True, port=8050, use_reloader=False)