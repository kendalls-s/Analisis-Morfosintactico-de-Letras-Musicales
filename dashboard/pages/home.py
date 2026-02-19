# -*- coding: utf-8 -*-
# Home page - project overview with navigation cards
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Inicio", order=0)

PAGES = [
    {"icon": "01", "title": "EDA",          "desc": "Distribucion de generos, artistas, anos y longitud de letras.", "href": "/eda",               "color": "#4A148C"},
    {"icon": "02", "title": "POS Tags",     "desc": "Tags NLTK y spaCy con comparacion entre modelos.",             "href": "/pos-distributions",  "color": "#7B1FA2"},
    {"icon": "03", "title": "Morfologico",  "desc": "Densidad lexica, categorias gramaticales por genero.",         "href": "/morphological",      "color": "#AB47BC"},
    {"icon": "04", "title": "Generos",      "desc": "Comparacion linguistica: verbos, sustantivos, riqueza.",       "href": "/genre-comparison",   "color": "#E91E8C"},
    {"icon": "05", "title": "Temporal",     "desc": "Evolucion de metricas linguisticas por ano y decada.",         "href": "/temporal-evolution", "color": "#7C4DFF"},
    {"icon": "06", "title": "Metricas",     "desc": "Resumen cuantitativo: tokens totales, tags unicos, spaCy.",    "href": "/metrics",            "color": "#880E4F"},
]

def nav_card(p):
    return dbc.Col(
        html.A(html.Div([
            html.Div([
                html.Span(p["icon"], style={
                    "fontFamily": "JetBrains Mono, monospace",
                    "fontSize": "0.65rem", "fontWeight": "700",
                    "background": p["color"], "color": "#FFFFFF",
                    "padding": "2px 6px", "borderRadius": "3px",
                    "marginBottom": "0.6rem", "display": "inline-block",
                }),
                html.H5(p["title"], style={
                    "fontFamily": "Inter, sans-serif", "fontWeight": "700",
                    "color": p["color"], "margin": "0 0 0.4rem", "fontSize": "1rem",
                }),
                html.P(p["desc"], style={
                    "fontFamily": "Inter, sans-serif", "fontSize": "0.78rem",
                    "color": "#5A7A8A", "margin": "0", "lineHeight": "1.5",
                }),
            ]),
            html.Div(style={
                "position": "absolute", "bottom": "0", "left": "0",
                "height": "3px", "width": "100%",
                "background": p["color"], "borderRadius": "0 0 10px 10px",
            }),
        ], style={
            "position": "relative", "background": "#FFFFFF",
            "border": "1px solid #D1A8E8", "borderRadius": "10px",
            "padding": "1.25rem", "height": "100%",
            "boxShadow": "0 1px 4px rgba(106,27,154,0.06)",
        }),
        href=p["href"], style={"textDecoration": "none", "display": "block", "height": "100%"}),
        xs=12, sm=6, lg=4, style={"marginBottom": "1rem"},
    )

layout = html.Div([
    html.Div([
        html.Div(style={
            "background": "linear-gradient(135deg, #4A148C 0%, #7B1FA2 50%, #E91E8C 100%)",
            "borderRadius": "14px", "padding": "2.5rem 2rem", "marginBottom": "2rem",
            "textAlign": "center",
        }, children=[
            html.H1("Analisis Morfosintactico", style={
                "fontFamily": "Inter, sans-serif", "fontWeight": "800",
                "fontSize": "clamp(1.6rem,3.5vw,2.4rem)", "color": "#FFFFFF", "margin": "0 0 0.4rem",
            }),
            html.H2("de Letras Musicales", style={
                "fontFamily": "Inter, sans-serif", "fontWeight": "400",
                "fontSize": "clamp(1rem,2vw,1.4rem)", "color": "#E8D5F5", "margin": "0 0 1rem",
            }),
            html.P("Exploracion linguistica del corpus con NLTK y spaCy - POS tagging, densidad lexica, comparacion de generos y evolucion temporal.",
                style={"fontFamily": "Inter, sans-serif", "fontSize": "0.85rem",
                       "color": "#F3E5F5", "maxWidth": "580px", "margin": "0 auto", "lineHeight": "1.6"}),
        ]),
    ]),

    dbc.Row([
        dbc.Col(html.Div([html.Div("7,936",  className="metric-value"), html.Div("Canciones", className="metric-label")], className="metric-card"), xs=6, md=3, style={"marginBottom":"1rem"}),
        dbc.Col(html.Div([html.Div("~2M+",   className="metric-value"), html.Div("Tokens spaCy", className="metric-label")], className="metric-card"), xs=6, md=3, style={"marginBottom":"1rem"}),
        dbc.Col(html.Div([html.Div("17",     className="metric-value"), html.Div("Categorias POS", className="metric-label")], className="metric-card"), xs=6, md=3, style={"marginBottom":"1rem"}),
        dbc.Col(html.Div([html.Div("8+",     className="metric-value"), html.Div("Generos Musicales", className="metric-label")], className="metric-card"), xs=6, md=3, style={"marginBottom":"1rem"}),
    ], className="g-2", style={"marginBottom": "1.5rem"}),

    html.P("Explorar el dashboard", style={
        "fontFamily": "JetBrains Mono, monospace", "fontSize": "0.7rem",
        "color": "#78909C", "textTransform": "uppercase", "letterSpacing": "0.12em",
        "marginBottom": "1rem",
    }),
    dbc.Row([nav_card(p) for p in PAGES], className="g-2"),
])
