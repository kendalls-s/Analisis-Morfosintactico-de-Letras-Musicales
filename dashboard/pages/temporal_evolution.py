# -*- coding: utf-8 -*-
# Temporal Evolution - notebook 06_evolucion_temporal
# Charts: song length evolution, TTR evolution, noun vs verb density,
#         smoothed noun vs verb (rolling 5yr), decade aggregations table
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_cache import yearly, decade_agg

dash.register_page(__name__, path="/temporal-evolution", name="Temporal", order=5)

BG = "#FFFFFF"; PLOT = "#FFFFFF"; GRID = "#D0E8F5"; FONT = "#1A2E3A"

def card(title, children):
    return html.Div([html.Div(title, className="section-title"), children], className="card-panel")

def fig_base(fig):
    fig.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG, font_color=FONT,
                      font_family="Inter", margin=dict(l=10,r=10,t=10,b=10))
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig

# -- Chart 1: Evolution of Average Song Length ---------------------------------
fig_len = go.Figure()
fig_len.add_trace(go.Scatter(x=yearly.index, y=yearly["song_length"],
    mode="lines", line=dict(color="#E1BEE7", width=1.2), name="Yearly avg", opacity=0.7))
fig_len.add_trace(go.Scatter(x=yearly.index, y=yearly["song_length"].rolling(5).mean(),
    mode="lines", line=dict(color="#6A1B9A", width=2.5), name="5-yr moving avg"))
fig_len.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG, font_color=FONT,
    font_family="Inter", margin=dict(l=10,r=10,t=10,b=10),
    xaxis_title="Year", yaxis_title="Average Length",
    legend=dict(font=dict(size=10)))
fig_len.update_xaxes(gridcolor=GRID); fig_len.update_yaxes(gridcolor=GRID)

# -- Chart 2: Evolution of Lexical Diversity (TTR) ----------------------------
fig_ttr = go.Figure()
fig_ttr.add_trace(go.Scatter(x=yearly.index, y=yearly["ttr"],
    mode="lines", line=dict(color="#E1BEE7", width=1.2), name="Yearly TTR", opacity=0.7))
fig_ttr.add_trace(go.Scatter(x=yearly.index, y=yearly["ttr"].rolling(5).mean(),
    mode="lines", line=dict(color="#8E24AA", width=2.5), name="5-yr moving avg"))
fig_ttr.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG, font_color=FONT,
    font_family="Inter", margin=dict(l=10,r=10,t=10,b=10),
    xaxis_title="Year", yaxis_title="TTR",
    legend=dict(font=dict(size=10)))
fig_ttr.update_xaxes(gridcolor=GRID); fig_ttr.update_yaxes(gridcolor=GRID)

# -- Chart 3: Noun vs Verb Density Over Time -----------------------------------
fig_nv = go.Figure()
fig_nv.add_trace(go.Scatter(x=yearly.index, y=yearly["noun_density"],
    mode="lines", line=dict(color="#6A1B9A", width=1.5), name="NOUN"))
fig_nv.add_trace(go.Scatter(x=yearly.index, y=yearly["verb_density"],
    mode="lines", line=dict(color="#CE93D8", width=1.5), name="VERB"))
fig_nv.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG, font_color=FONT,
    font_family="Inter", margin=dict(l=10,r=10,t=10,b=10),
    xaxis_title="Year", yaxis_title="Density",
    legend=dict(font=dict(size=10)))
fig_nv.update_xaxes(gridcolor=GRID); fig_nv.update_yaxes(gridcolor=GRID)

# -- Chart 4: Smoothed Noun vs Verb Density (rolling 5yr) ---------------------
_rn = yearly["noun_density"].rolling(window=5).mean()
_rv = yearly["verb_density"].rolling(window=5).mean()
fig_smooth = go.Figure()
fig_smooth.add_trace(go.Scatter(x=yearly.index, y=_rn,
    mode="lines", line=dict(color="#6A1B9A", width=2.5), name="NOUN (5-year MA)"))
fig_smooth.add_trace(go.Scatter(x=yearly.index, y=_rv,
    mode="lines", line=dict(color="#AB47BC", width=2.5), name="VERB (5-year MA)"))
fig_smooth.update_layout(plot_bgcolor=PLOT, paper_bgcolor=BG, font_color=FONT,
    font_family="Inter", margin=dict(l=10,r=10,t=10,b=10),
    xaxis_title="Year", yaxis_title="Density",
    legend=dict(font=dict(size=10)))
fig_smooth.update_xaxes(gridcolor=GRID); fig_smooth.update_yaxes(gridcolor=GRID)

# -- Table: decade_metrics (notebook cell: decade_metrics) --------------------
_dec_rows = []
for _, row in decade_agg.iterrows():
    _dec_rows.append(html.Tr([
        html.Td(str(int(row["decade"])),           style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.76rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","fontWeight":"600","color":"#6A1B9A"}),
        html.Td(f"{row['song_length']:.1f}",       style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.76rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right"}),
        html.Td(f"{row['ttr']:.4f}",               style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.76rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right"}),
        html.Td(f"{row['noun_density']:.4f}",      style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.76rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right"}),
        html.Td(f"{row['verb_density']:.4f}",      style={"fontFamily":"JetBrains Mono,monospace","fontSize":"0.76rem","padding":"0.3rem 0.5rem","border":"1px solid #D0E8F5","textAlign":"right"}),
    ]))

layout = html.Div([
    html.H2("Evolucion Temporal"),
    html.P("Como han cambiado las metricas linguisticas de las letras musicales (notebook 06_evolucion_temporal)",
           className="page-sub"),
    dbc.Row([
        dbc.Col(card("Evolution of Average Song Length",    dcc.Graph(figure=fig_len,    config={"displayModeBar":False}, style={"height":"270px"})), md=6),
        dbc.Col(card("Evolution of Lexical Diversity (TTR)", dcc.Graph(figure=fig_ttr,   config={"displayModeBar":False}, style={"height":"270px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col(card("Noun vs Verb Density Over Time",          dcc.Graph(figure=fig_nv,     config={"displayModeBar":False}, style={"height":"270px"})), md=6),
        dbc.Col(card("Smoothed Noun vs Verb Density (5-yr MA)", dcc.Graph(figure=fig_smooth, config={"displayModeBar":False}, style={"height":"270px"})), md=6),
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            html.Div("Aggregation por Decada (decade_metrics)", className="section-title"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Decada",       style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A"}),
                    html.Th("Song Length",  style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A","textAlign":"right"}),
                    html.Th("TTR",          style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A","textAlign":"right"}),
                    html.Th("Noun Density", style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A","textAlign":"right"}),
                    html.Th("Verb Density", style={"fontFamily":"Inter","fontSize":"0.75rem","padding":"0.35rem 0.5rem","border":"1px solid #D0E8F5","background":"#FCF0FF","color":"#6A1B9A","textAlign":"right"}),
                ])),
                html.Tbody(_dec_rows),
            ], style={"width":"100%","borderCollapse":"collapse"}),
        ], className="card-panel", md=12),
    ], className="g-0"),
])
