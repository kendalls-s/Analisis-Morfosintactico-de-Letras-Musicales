"""
chatbot_app.py
──────────────
GenreBot — Chatbot Musical con RAG + MongoDB
Lanzar con: python dashboard_p02_/chatbot_app.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from src.Proyecto_3.rag_utils import construir_indice, stats_corpus
from src.Proyecto_3.chatbot_engine import ChatbotMusical

# ── Inicialización desde MongoDB ──────────────────────────────────────────────
print("Conectando a MongoDB y construyendo índice RAG...")
construir_indice()

STATS = stats_corpus()
print(f"Corpus: {STATS}")

bot = ChatbotMusical()
print("GenreBot listo en http://localhost:8050")

# ── Paleta azul ───────────────────────────────────────────────────────────────
AZUL_OSCURO  = "#050d1a"
AZUL_MEDIO   = "#0a1628"
AZUL_PANEL   = "#0d1f3c"
AZUL_BORDE   = "rgba(56, 139, 253, 0.2)"
AZUL_ACENTO  = "#388bfd"
AZUL_CLARO   = "#58a6ff"
TEXTO        = "#cdd9e5"
TEXTO_SUAVE  = "#8b949e"

GENRE_BADGES = {
    "Rock":    ("🎸", "#58a6ff"),
    "Hip-Hop": ("🎤", "#79c0ff"),
    "Metal":   ("🤘", "#388bfd"),
}

# ── App Dash ──────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="GenreBot — Chatbot Musical",
)
server = app.server

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar = html.Div(style={
    "width": "260px", "minHeight": "100vh",
    "background": AZUL_PANEL,
    "borderRight": f"1px solid {AZUL_BORDE}",
    "padding": "2rem 1.5rem",
    "display": "flex", "flexDirection": "column", "gap": "1.5rem",
}, children=[
    html.Div([
        html.Div("GENRE", style={
            "fontFamily": "'Orbitron', sans-serif",
            "fontSize": "2rem", "fontWeight": "900",
            "letterSpacing": "0.1em", "color": AZUL_CLARO,
            "lineHeight": "1", "textShadow": f"0 0 20px {AZUL_ACENTO}",
        }),
        html.Div("BOT", style={
            "fontFamily": "'Orbitron', sans-serif",
            "fontSize": "2rem", "fontWeight": "900",
            "letterSpacing": "0.1em", "color": "#fff",
            "lineHeight": "1",
        }),
        html.Div("Experto en géneros musicales", style={
            "fontFamily": "'Rajdhani', sans-serif",
            "fontSize": "0.75rem", "color": TEXTO_SUAVE,
            "marginTop": "0.5rem", "letterSpacing": "0.05em",
        }),
    ]),

    html.Hr(style={"borderColor": AZUL_BORDE}),

    html.Div("GÉNEROS", style={
        "fontFamily": "'Rajdhani', sans-serif",
        "fontSize": "0.65rem", "color": TEXTO_SUAVE,
        "letterSpacing": "0.15em", "fontWeight": "600",
    }),
    html.Div([
        html.Div([
            html.Span(icon, style={"marginRight": "8px"}),
            html.Span(genre, style={
                "color": color, "fontWeight": "600",
                "fontFamily": "'Rajdhani', sans-serif",
                "fontSize": "0.95rem",
            }),
        ], style={"padding": "0.5rem 0", "borderBottom": f"1px solid {AZUL_BORDE}"})
        for genre, (icon, color) in GENRE_BADGES.items()
    ]),

    html.Hr(style={"borderColor": AZUL_BORDE}),

    html.Div("CORPUS (MongoDB)", style={
        "fontFamily": "'Rajdhani', sans-serif",
        "fontSize": "0.65rem", "color": TEXTO_SUAVE,
        "letterSpacing": "0.15em", "fontWeight": "600",
    }),
    html.Div([
        html.Div(f"🎵 {STATS.get('total', 0):,} canciones",
                 style={"fontSize": "0.85rem", "color": TEXTO,
                        "fontFamily": "'Rajdhani', sans-serif"}),
        html.Div(f"🎸 {STATS.get('Rock', 0):,} Rock",
                 style={"fontSize": "0.8rem", "color": AZUL_CLARO,
                        "fontFamily": "'Rajdhani', sans-serif"}),
        html.Div(f"🎤 {STATS.get('Hip-Hop', 0):,} Hip-Hop",
                 style={"fontSize": "0.8rem", "color": "#79c0ff",
                        "fontFamily": "'Rajdhani', sans-serif"}),
        html.Div(f"🤘 {STATS.get('Metal', 0):,} Metal",
                 style={"fontSize": "0.8rem", "color": AZUL_ACENTO,
                        "fontFamily": "'Rajdhani', sans-serif"}),
    ], style={"display": "flex", "flexDirection": "column", "gap": "0.4rem"}),

    html.Div(style={"flex": "1"}),

    html.Div([
        html.Span("🟢 ", style={"color": "#3fb950"}),
        html.Span("MongoDB conectado", style={
            "fontSize": "0.7rem", "color": "#3fb950",
            "fontFamily": "'Rajdhani', sans-serif",
        }),
    ]),

    dbc.Button("🗑️ Limpiar chat", id="btn-clear", color="primary",
               outline=True, size="sm",
               style={
                   "fontFamily": "'Rajdhani', sans-serif",
                   "fontSize": "0.8rem", "fontWeight": "600",
                   "borderColor": AZUL_ACENTO, "color": AZUL_CLARO,
               }),
])

# ── Main content ──────────────────────────────────────────────────────────────
main_content = html.Div(style={
    "flex": "1", "display": "flex", "flexDirection": "column",
    "padding": "2rem", "maxWidth": "900px", "margin": "0 auto", "width": "100%",
}, children=[
    html.Div([
        html.Div("Chat con GenreBot", style={
            "fontFamily": "'Orbitron', sans-serif",
            "fontSize": "1.5rem", "fontWeight": "700",
            "color": "#fff", "letterSpacing": "0.05em",
        }),
        html.Div("Pregúntame sobre Rock, Hip-Hop y Metal · Powered by RAG + DistilBERT",
                 style={
                     "fontFamily": "'Rajdhani', sans-serif",
                     "fontSize": "0.8rem", "color": TEXTO_SUAVE,
                 }),
    ], style={"marginBottom": "1.5rem"}),

    html.Div(id="chat-display", style={
        "flex": "1", "overflowY": "auto",
        "background": AZUL_MEDIO,
        "borderRadius": "12px",
        "border": f"1px solid {AZUL_BORDE}",
        "padding": "1.5rem",
        "minHeight": "450px", "maxHeight": "550px",
        "marginBottom": "1rem",
    }, children=[
        html.Div([
            html.Span("🤖 GenreBot", style={
                "fontFamily": "'Rajdhani', sans-serif",
                "fontSize": "0.7rem", "color": AZUL_CLARO,
                "display": "block", "marginBottom": "4px", "fontWeight": "600",
            }),
            html.Span("¡Hola! Soy GenreBot, tu experto en géneros musicales. "
                      "Tengo acceso a tu corpus en MongoDB con canciones de "
                      "Rock, Hip-Hop y Metal. ¿Qué quieres saber?",
                      style={"fontFamily": "'Rajdhani', sans-serif",
                             "fontSize": "0.95rem", "color": TEXTO}),
        ], style={
            "background": "rgba(56,139,253,0.08)",
            "border": f"1px solid {AZUL_BORDE}",
            "borderRadius": "8px", "padding": "1rem",
        })
    ]),

    html.Div(style={"display": "flex", "gap": "0.75rem", "alignItems": "center"}, children=[
        dcc.Input(
            id="user-input", type="text",
            placeholder="Escribe tu pregunta sobre música...",
            debounce=False, n_submit=0,
            style={
                "flex": "1",
                "background": AZUL_PANEL,
                "border": f"1px solid {AZUL_BORDE}",
                "borderRadius": "8px", "padding": "0.75rem 1rem",
                "color": "#fff",
                "fontFamily": "'Rajdhani', sans-serif",
                "fontSize": "0.95rem", "outline": "none",
            }
        ),
        dbc.Button("Enviar →", id="btn-send", color="primary", style={
            "fontFamily": "'Rajdhani', sans-serif",
            "fontSize": "0.9rem", "fontWeight": "700",
            "padding": "0.75rem 1.5rem", "borderRadius": "8px",
            "background": AZUL_ACENTO, "borderColor": AZUL_ACENTO,
        }),
    ]),

    html.Div([
        html.Div("Prueba estas preguntas:",
                 style={
                     "fontFamily": "'Rajdhani', sans-serif",
                     "fontSize": "0.7rem", "color": TEXTO_SUAVE,
                     "marginTop": "1rem", "marginBottom": "0.5rem",
                 }),
        html.Div([
            dbc.Button(q, id={"type": "suggested", "index": i},
                      color="primary", outline=True, size="sm",
                      style={
                          "fontFamily": "'Rajdhani', sans-serif",
                          "fontSize": "0.75rem", "margin": "2px",
                          "borderColor": AZUL_BORDE, "color": AZUL_CLARO,
                      })
for i, q in enumerate([
    "¿Qué canciones de Rock hablan de libertad?",
    "Háblame de los temas del Metal",
    "¿Qué artistas de Hip-Hop hay en el corpus?",
    "¿Cuál es la diferencia entre Rock y Metal?",
])
        ]),
    ]),

    dcc.Store(id="chat-history", data=[]),
])

app.layout = html.Div(style={
    "minHeight": "100vh",
    "background": f"linear-gradient(160deg, {AZUL_OSCURO} 0%, #071428 50%, {AZUL_MEDIO} 100%)",
    "fontFamily": "'Rajdhani', sans-serif",
    "color": TEXTO,
}, children=[
    html.Div(style={"display": "flex", "minHeight": "100vh"}, children=[
        sidebar,
        main_content,
    ])
])


# ── Helpers ───────────────────────────────────────────────────────────────────

def render_mensaje(texto, es_usuario=True):
    if es_usuario:
        return html.Div([
            html.Span("👤 Tú", style={
                "fontFamily": "'Rajdhani', sans-serif",
                "fontSize": "0.7rem", "color": TEXTO_SUAVE,
                "display": "block", "marginBottom": "4px", "fontWeight": "600",
            }),
            html.Div(texto, style={
                "color": "#fff",
                "fontFamily": "'Rajdhani', sans-serif",
                "fontSize": "0.95rem",
            }),
        ], style={
            "background": "rgba(255,255,255,0.04)",
            "border": "1px solid rgba(255,255,255,0.08)",
            "borderRadius": "8px", "padding": "0.75rem 1rem",
            "marginBottom": "0.75rem", "marginLeft": "2rem",
        })
    else:
        lineas = texto.split("\n")
        contenido = []
        for linea in lineas:
            if linea.startswith("📀"):
                contenido.append(html.Div(linea, style={
                    "fontFamily": "'Rajdhani', sans-serif",
                    "fontSize": "0.75rem", "color": TEXTO_SUAVE,
                    "marginTop": "0.5rem",
                    "borderTop": f"1px solid {AZUL_BORDE}",
                    "paddingTop": "0.5rem",
                }))
            elif linea.startswith("•"):
                contenido.append(html.Div(linea, style={
                    "fontFamily": "'Rajdhani', sans-serif",
                    "fontSize": "0.8rem", "color": AZUL_CLARO,
                    "paddingLeft": "0.5rem",
                }))
            elif "**" in linea:
                contenido.append(html.Div(linea.replace("**", ""), style={
                    "fontFamily": "'Rajdhani', sans-serif",
                    "fontSize": "0.95rem", "color": AZUL_CLARO,
                    "fontWeight": "700",
                }))
            else:
                contenido.append(html.Div(linea, style={
                    "color": TEXTO,
                    "fontFamily": "'Rajdhani', sans-serif",
                    "fontSize": "0.95rem",
                }))

        return html.Div([
            html.Span("BotByGenre", style={
                "fontFamily": "'Rajdhani', sans-serif",
                "fontSize": "0.7rem", "color": AZUL_CLARO,
                "display": "block", "marginBottom": "4px", "fontWeight": "600",
            }),
            html.Div(contenido),
        ], style={
            "background": "rgba(56,139,253,0.06)",
            "border": f"1px solid {AZUL_BORDE}",
            "borderRadius": "8px", "padding": "0.75rem 1rem",
            "marginBottom": "0.75rem", "marginRight": "2rem",
        })


# ── Callbacks ─────────────────────────────────────────────────────────────────

@app.callback(
    Output("user-input", "value"),
    [Input({"type": "suggested", "index": i}, "n_clicks") for i in range(4)],
    prevent_initial_call=True,
)
def fill_suggested(*args):
    preguntas = [
        "¿Qué canciones de Rock hablan de libertad?",
        "Háblame de los temas del Metal",
        "¿Qué artistas de Hip-Hop hay en el corpus?",
        "¿Cuál es la diferencia entre Rock y Metal?",
    ]
    ctx = callback_context
    if not ctx.triggered:
        return ""
    idx = eval(ctx.triggered[0]["prop_id"].split(".")[0])["index"]
    return preguntas[idx]


@app.callback(
    Output("chat-display", "children"),
    Output("chat-history", "data"),
    Output("user-input", "value", allow_duplicate=True),
    Input("btn-send", "n_clicks"),
    Input("user-input", "n_submit"),
    Input("btn-clear", "n_clicks"),
    State("user-input", "value"),
    State("chat-history", "data"),
    prevent_initial_call=True,
)
def actualizar_chat(n_send, n_submit, n_clear, texto, historial):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update

    trigger = ctx.triggered[0]["prop_id"]

    if "btn-clear" in trigger:
        bot.limpiar_historial()
        return [html.Div([
            html.Span("🤖 GenreBot", style={
                "fontFamily": "'Rajdhani', sans-serif",
                "fontSize": "0.7rem", "color": AZUL_CLARO,
                "display": "block", "marginBottom": "4px", "fontWeight": "600",
            }),
            html.Span("Chat limpiado. ¿En qué puedo ayudarte?",
                      style={"fontFamily": "'Rajdhani', sans-serif",
                             "fontSize": "0.95rem"}),
        ], style={
            "background": "rgba(56,139,253,0.08)",
            "border": f"1px solid {AZUL_BORDE}",
            "borderRadius": "8px", "padding": "1rem",
        })], [], ""

    if not texto or not texto.strip():
        return dash.no_update, dash.no_update, ""

    respuesta = bot.responder(texto.strip())
    historial = historial or []
    historial.append({"usuario": texto.strip(), "bot": respuesta})

    mensajes = [html.Div([
        html.Span("🤖 GenreBot", style={
            "fontFamily": "'Rajdhani', sans-serif",
            "fontSize": "0.7rem", "color": AZUL_CLARO,
            "display": "block", "marginBottom": "4px", "fontWeight": "600",
        }),
        html.Span("¡Hola! Soy GenreBot, tu experto en géneros musicales. "
                  "Tengo acceso a tu corpus en MongoDB con canciones de "
                  "Rock, Hip-Hop y Metal. ¿Qué quieres saber?",
                  style={"fontFamily": "'Rajdhani', sans-serif",
                         "fontSize": "0.95rem", "color": TEXTO}),
    ], style={
        "background": "rgba(56,139,253,0.08)",
        "border": f"1px solid {AZUL_BORDE}",
        "borderRadius": "8px", "padding": "1rem", "marginBottom": "0.75rem",
    })]

    for turno in historial:
        mensajes.append(render_mensaje(turno["usuario"], es_usuario=True))
        mensajes.append(render_mensaje(turno["bot"],     es_usuario=False))

    return mensajes, historial, ""


if __name__ == "__main__":
    app.run(debug=False, port=8050)