# -*- coding: utf-8 -*-
# EDA page - notebook 01_exploracion_datos.ipynb
# Charts: genre bar, top artists bar, year histogram, decade bar,
#         lyrics length describe + histogram, boxplot by genre, corr heatmap,
#         avg length per year lineplot, boxplots outliers
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_cache import df_clean

dash.register_page(__name__, path="/eda", name="EDA", order=1)

BG   = "#FFFFFF"
PLOT = "#FFFFFF"
GRID = "#D0E8F5"
FONT = "#1A2E3A"
PAL = ["#4A148C","#7B1FA2","#E91E8C","#7C4DFF","#AB47BC","#880E4F","#CE93D8","#FF4081","#9C27B0","#D500F9"]

T = dict(template="plotly_white", font_family="Inter")

def card(title, children):
    return html.Div([html.Div(title, className="section-title"), children], className="card-panel")

def fig_layout(fig):
    fig.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG,
                      font_color=FONT, font_family="Inter",
                      margin=dict(l=10, r=10, t=10, b=10))
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig

# -- Chart 1: Cantidad de canciones por genero (notebook cell 1) --------------
_gc = df_clean["Genre"].value_counts().reset_index()
_gc.columns = ["Genre", "count"]
fig_genre = fig_layout(px.bar(_gc, x="count", y="Genre", orientation="h",
    color="Genre", color_discrete_sequence=PAL,
    labels={"count": "Numero de canciones", "Genre": ""}))
fig_genre.update_layout(showlegend=False, yaxis=dict(categoryorder="total ascending"))

# -- Chart 2: Top 20 artistas (notebook cell 2) --------------------------------
_ta = df_clean["Artist"].value_counts().head(20).reset_index()
_ta.columns = ["Artist", "count"]
fig_artists = fig_layout(px.bar(_ta, x="count", y="Artist", orientation="h",
    color="count", color_continuous_scale="Purples",
    labels={"count": "Cantidad de canciones", "Artist": ""}))
fig_artists.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))

# -- Chart 3: Distribucion de anos (notebook cell 3) ---------------------------
fig_years = fig_layout(px.histogram(df_clean, x="Song year", nbins=30,
    color_discrete_sequence=["#7B1FA2"],
    labels={"Song year": "Ano", "count": "Frecuencia"}))
fig_years.update_layout(bargap=0.05)

# -- Chart 4: Canciones por decada (notebook cell 4) --------------------------
_dc = df_clean["Decade"].value_counts().sort_index().reset_index()
_dc.columns = ["Decade", "count"]
fig_decade = fig_layout(px.bar(_dc, x="Decade", y="count",
    color="count", color_continuous_scale="Purples",
    labels={"Decade": "Decada", "count": "Cantidad"}))
fig_decade.update_layout(coloraxis_showscale=False)

# -- Chart 5: Histograma longitud de letras (notebook cell 5) -----------------
_desc = df_clean["Lyrics_length"].describe().round(2)
fig_hist_len = fig_layout(px.histogram(df_clean, x="Lyrics_length", nbins=50,
    color_discrete_sequence=["#CE93D8"],
    labels={"Lyrics_length": "Palabras", "count": "Frecuencia"}))
fig_hist_len.update_layout(bargap=0.03)

# -- Chart 6: Boxplot longitud por genero (notebook cell 6) -------------------
fig_box = fig_layout(px.box(df_clean, x="Genre", y="Lyrics_length",
    color="Genre", color_discrete_sequence=PAL,
    labels={"Genre": "Genero", "Lyrics_length": "Numero de palabras"}))
fig_box.update_layout(showlegend=False)

# -- Chart 7: Heatmap correlacion ano vs longitud (notebook cell 7) -----------
_corr = df_clean[["Song year", "Lyrics_length"]].corr()
fig_corr = go.Figure(data=go.Heatmap(
    z=_corr.values, x=_corr.columns.tolist(), y=_corr.index.tolist(),
    colorscale="RdBu", zmid=0, showscale=True,
    text=_corr.values.round(3), texttemplate="%{text}",
))
fig_corr.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG,
    font_color=FONT, font_family="Inter", margin=dict(l=10,r=10,t=10,b=10))

# -- Chart 8: Longitud media por ano lineplot (notebook cell 8) ---------------
_avg = df_clean.groupby("Song year")["Lyrics_length"].mean().reset_index()
fig_avg = fig_layout(px.line(_avg, x="Song year", y="Lyrics_length",
    color_discrete_sequence=["#6A1B9A"],
    labels={"Song year": "Ano", "Lyrics_length": "Palabras promedio"}))
fig_avg.update_traces(line_width=2)

# -- Chart 9: Boxplots outliers Song year + Lyrics_length (notebook cell 9) ---
fig_box2 = go.Figure()
fig_box2.add_trace(go.Box(y=df_clean["Song year"], name="Anos", marker_color="#7B1FA2"))
fig_box2.add_trace(go.Box(y=df_clean["Lyrics_length"], name="Longitud letras", marker_color="#7C4DFF"))
fig_box2.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG,
    font_color=FONT, font_family="Inter", margin=dict(l=10,r=10,t=10,b=10))
fig_box2.update_xaxes(gridcolor=GRID); fig_box2.update_yaxes(gridcolor=GRID)

# -- Stats table (notebook: df['Lyrics_length'].describe()) -------------------
_stats = df_clean["Lyrics_length"].describe().round(2).reset_index()
_stats.columns = ["Estadistico", "Valor"]
_stat_rows = [html.Tr([
    html.Td(r["Estadistico"], style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.78rem","padding":"0.35rem 0.6rem","border":"1px solid #D0E8F5"}),
    html.Td(str(r["Valor"]),  style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.78rem","padding":"0.35rem 0.6rem","border":"1px solid #D0E8F5","textAlign":"right","fontWeight":"600","color":"#6A1B9A"}),
]) for _, r in _stats.iterrows()]

_total = len(df_clean); _genres = df_clean["Genre"].nunique()
_artists = df_clean["Artist"].nunique(); _avg_w = int(df_clean["Lyrics_length"].mean())

# -- Layout --------------------------------------------------------------------
layout = html.Div([
    html.H2("EDA - Exploracion de Datos"),
    html.P("Analisis exploratorio del corpus de letras musicales (notebook 01_exploracion_datos)",
           className="page-sub"),
    dbc.Row([
        dbc.Col(html.Div([html.Div(f"{_total:,}", className="metric-value"), html.Div("Canciones", className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(str(_genres), className="metric-value"), html.Div("Generos", className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(f"{_artists:,}", className="metric-value"), html.Div("Artistas", className="metric-label")], className="metric-card"), xs=6, md=3),
        dbc.Col(html.Div([html.Div(f"{_avg_w:,}", className="metric-value"), html.Div("Palabras promedio", className="metric-label")], className="metric-card"), xs=6, md=3),
    ], className="g-2", style={"marginBottom": "1.25rem"}),

    dbc.Row([
        dbc.Col(card("Cantidad de canciones por genero", dcc.Graph(figure=fig_genre,   config={"displayModeBar":False}, style={"height":"300px"})), md=6),
        dbc.Col(card("Top 20 artistas con mas canciones", dcc.Graph(figure=fig_artists, config={"displayModeBar":False}, style={"height":"300px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Distribucion de anos de las canciones", dcc.Graph(figure=fig_years,  config={"displayModeBar":False}, style={"height":"240px"})), md=6),
        dbc.Col(card("Canciones por decada",                   dcc.Graph(figure=fig_decade, config={"displayModeBar":False}, style={"height":"240px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Distribucion longitud de letras (num. palabras)", dcc.Graph(figure=fig_hist_len, config={"displayModeBar":False}, style={"height":"250px"})), md=8),
        dbc.Col([
            html.Div("Estadisticas: Lyrics_length", className="section-title"),
            html.Table(_stat_rows, style={"width":"100%","borderCollapse":"collapse","background":"#FFFFFF"}),
        ], className="card-panel", md=4),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Longitud de letras por genero musical", dcc.Graph(figure=fig_box,  config={"displayModeBar":False}, style={"height":"280px"})), md=8),
        dbc.Col(card("Correlacion ano vs longitud",           dcc.Graph(figure=fig_corr, config={"displayModeBar":False}, style={"height":"280px"})), md=4),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Longitud media de letras por ano",      dcc.Graph(figure=fig_avg,  config={"displayModeBar":False}, style={"height":"240px"})), md=6),
        dbc.Col(card("Boxplot valores atipicos (anos y longitud)", dcc.Graph(figure=fig_box2, config={"displayModeBar":False}, style={"height":"240px"})), md=6),
    ], className="g-0"),
])
