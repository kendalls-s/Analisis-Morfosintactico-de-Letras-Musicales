"""pages/comparacion.py — Comparación Final: TF-IDF vs Word2Vec vs BERT"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from data import (base_layout, PALETTE, GENRE_COLORS, GENRES,
                  get_clf_results, get_silhouette_results,
                  get_f1_heatmap, get_confusion_matrix, get_comp_tsne,
                  _load_embedding_data)

dash.register_page(__name__, path="/comparacion", title="Comparación Final")

def kpi(value, label, sub, accent=False):
    return html.Div(className=f"kpi-card{'  accent-card' if accent else ''}", children=[
        html.Div(value, className="kpi-val"),
        html.Div(label, className="kpi-label"),
        html.Div(sub,   className="kpi-sub"),
    ])

def card(title, tag, cid, tall=False, xl=False, full=False):
    body = "chart-body" + (" chart-tall" if tall else "") + (" chart-xl" if xl else "")
    return html.Div(className=f"chart-card{'  full-width' if full else ''}", children=[
        html.Div(className="chart-header", children=[
            html.H3(title), html.Span(tag, className="chart-tag")]),
        dcc.Graph(id=cid, className=body, config={"displayModeBar": False}),
    ])

layout = html.Div(className="page-inner", children=[
    html.Div(className="section-intro", children=[
        html.Div(children=[
            html.H2("Comparación Final: TF-IDF · Word2Vec · BERT"),
            html.P("Evaluación con Regresión Logística y KNN (k=5) sobre partición 80/20 "
                   "estratificada · 9,228 canciones · 10 géneros. "
                   "K-Means + Silhouette Score para evaluar separabilidad sin etiquetas."),
        ]),
    ]),

    html.Div(id="comp-kpi-row", className="kpi-row"),

    html.Div(className="grid-2", children=[
        card("Accuracy — Logistic Regression", "80/20 estratificado", "fig-comp-lr"),
        card("Accuracy — KNN (k=5, coseno)",   "80/20 estratificado", "fig-comp-knn"),
    ]),

    card("Silhouette Score — K-Means Clustering",
         "k = 10 géneros · métrica coseno", "fig-comp-sil"),

    card("F1-Score por Representación y Género",
         "Logistic Regression · verde = mayor F1",
         "fig-comp-f1", tall=True, full=True),

    html.Div(className="grid-2", children=[
        card("Dispersión TF-IDF vs Densidad BERT",
             "Dimensionalidad y dispersión de cada representación",
             "fig-comp-sparsity", tall=True),
    ]),

    card("t-SNE Comparativo: TF-IDF vs Word2Vec vs BERT",
         "Mismas canciones proyectadas a 2D con cada representación",
         "fig-comp-tsne", xl=True, full=True),
])

# ── Callbacks ──────────────────────────────────────────────────────────────────

@callback(Output("comp-kpi-row","children"), Input("comp-kpi-row","id"))
def render_kpis(_):
    df  = get_clf_results()
    sil = get_silhouette_results()
    tfidf_lr  = float(df[df["rep"]=="TF-IDF"]["lr"].values[0])
    w2v_lr    = float(df[df["rep"]=="Word2Vec"]["lr"].values[0])
    bert_lr   = float(df[df["rep"]=="BERT"]["lr"].values[0])
    mejora    = bert_lr - tfidf_lr
    return [
        kpi(f"{tfidf_lr*100:.1f}%",  "TF-IDF Accuracy",      "Logistic Regression"),
        kpi(f"{w2v_lr*100:.1f}%",    "Word2Vec Accuracy",     "Logistic Regression"),
        kpi(f"{bert_lr*100:.1f}%",   "BERT Accuracy",         "Mejor resultado", accent=True),
        kpi(f"+{mejora*100:.2f} pp", "Mejora BERT vs TF-IDF", "Ganancia por representación contextual"),
    ]

@callback(Output("fig-comp-lr","figure"), Input("fig-comp-lr","id"))
def fig_lr(_):
    df = get_clf_results()
    fig = go.Figure(go.Bar(
        x=df["rep"], y=df["lr"],
        marker=dict(color=df["color"].tolist(), opacity=.9),
        text=[f"{v*100:.1f}%" for v in df["lr"]], textposition="outside",
        textfont=dict(color=PALETTE["text"],size=13),
        hovertemplate="<b>%{x}</b><br>Accuracy: %{y:.1%}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=30,r=20,b=40,l=55),
        yaxis=dict(range=[0,.55], tickformat=".0%",
                   title=dict(text="Accuracy",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["muted"])),
        xaxis=dict(gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["text"])),
    ))
    return fig

@callback(Output("fig-comp-knn","figure"), Input("fig-comp-knn","id"))
def fig_knn(_):
    df = get_clf_results()
    fig = go.Figure(go.Bar(
        x=df["rep"], y=df["knn"],
        marker=dict(color=df["color"].tolist(), opacity=.9),
        text=[f"{v*100:.1f}%" for v in df["knn"]], textposition="outside",
        textfont=dict(color=PALETTE["text"],size=13),
        hovertemplate="<b>%{x}</b><br>KNN Accuracy: %{y:.1%}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=30,r=20,b=40,l=55),
        yaxis=dict(range=[0,.45], tickformat=".0%",
                   title=dict(text="Accuracy",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["muted"])),
        xaxis=dict(gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["text"])),
    ))
    return fig

@callback(Output("fig-comp-sil","figure"), Input("fig-comp-sil","id"))
def fig_sil(_):
    df = get_silhouette_results()
    fig = go.Figure(go.Bar(
        x=df["rep"], y=df["score"],
        marker=dict(color=df["color"].tolist(), opacity=.9),
        text=[f"{v:.4f}" for v in df["score"]], textposition="outside",
        textfont=dict(color=PALETTE["text"],size=13),
        hovertemplate="<b>%{x}</b><br>Silhouette: %{y:.4f}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=30,r=20,b=40,l=55),
        yaxis=dict(range=[-0.01,.10],
                   title=dict(text="Silhouette Score (coseno)",
                               font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["muted"])),
        xaxis=dict(gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["text"])),
    ))
    return fig

@callback(Output("fig-comp-f1","figure"), Input("fig-comp-f1","id"))
def fig_f1(_):
    df   = get_f1_heatmap()
    reps = ["TF-IDF","Word2Vec","BERT"]
    gens = sorted(df["genre"].unique().tolist())   # orden alfabético = mismo que notebook
    z = [[df[(df["rep"]==r)&(df["genre"]==g)]["f1"].values[0]
          if len(df[(df["rep"]==r)&(df["genre"]==g)]) > 0 else 0
          for g in gens] for r in reps]
    cs = [[0,"#3d1515"],[.3,"#8b4c4c"],[.6,PALETTE["gold"]],[1,PALETTE["cool"]]]
    fig = go.Figure(go.Heatmap(
        z=z, x=gens, y=reps, colorscale=cs,
        hovertemplate="<b>%{y}</b> · %{x}<br>F1: %{z:.3f}<extra></extra>",
        showscale=True, colorbar=dict(tickfont=dict(color=PALETTE["muted"],size=9),thickness=12),
        text=[[f"{v:.2f}" for v in row] for row in z],
        texttemplate="%{text}", textfont=dict(size=10,color="white"),
    ))
    fig.update_layout(**base_layout(margin=dict(t=10,r=70,b=70,l=100)))
    return fig

@callback(Output("fig-comp-confusion","figure"), Input("fig-comp-confusion","id"))
def fig_confusion(_):
    df = get_confusion_matrix()
    fig = go.Figure(go.Heatmap(
        z=df.values.tolist(), x=df.columns.tolist(), y=df.index.tolist(),
        colorscale=[[0,"#0d0e12"],[.5,PALETTE["accent"]+"77"],[1,PALETTE["accent"]]],
        hovertemplate="Real: <b>%{y}</b><br>Pred: <b>%{x}</b><br>N = %{z}<extra></extra>",
        showscale=False,
        text=df.values.tolist(), texttemplate="%{text}",
        textfont=dict(size=9,color=PALETTE["text"]),
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=10,r=20,b=80,l=100),
        xaxis=dict(tickangle=-35, gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["text"])),
        yaxis=dict(gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["text"])),
    ))
    return fig

@callback(Output("fig-comp-sparsity","figure"), Input("fig-comp-sparsity","id"))
def fig_sparsity(_):
    # TF-IDF=5000 dims, 96.8% sparse | W2V=100 dims, 0% | BERT=768 dims, 0%
    dims   = [5000, 100, 768]
    spars  = [96.8,  0.0, 0.0]
    names  = ["TF-IDF","Word2Vec","BERT"]
    colors = [PALETTE["muted"], PALETTE["warm"], PALETTE["accent"]]
    sizes  = [30, 20, 25]
    fig = go.Figure(go.Scatter(
        x=dims, y=spars, mode="markers+text", text=names,
        textposition="top center", textfont=dict(color=PALETTE["text"],size=13),
        marker=dict(color=colors, size=sizes, opacity=.88),
        hovertemplate="<b>%{text}</b><br>Dimensiones: %{x:,}<br>Dispersión: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        margin=dict(t=40,r=50,b=55,l=70),
        xaxis=dict(type="log",
                   title=dict(text="Dimensionalidad (log)",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["muted"])),
        yaxis=dict(range=[-5,108],
                   title=dict(text="Dispersión (%)",font=dict(size=10,color=PALETTE["muted"])),
                   gridcolor=PALETTE["border"],zeroline=False,
                   tickfont=dict(color=PALETTE["muted"])),
    ))
    return fig

@callback(Output("fig-comp-tsne","figure"), Input("fig-comp-tsne","id"))
def fig_tsne(_):
    import plotly.subplots as sp
    tsne_data = get_comp_tsne()
    reps = ["TF-IDF","Word2Vec","BERT"]
    fig  = sp.make_subplots(rows=1, cols=3, subplot_titles=reps,
                             horizontal_spacing=0.05)
    for col_idx, rep in enumerate(reps, 1):
        df = tsne_data.get(rep)
        if df is None:
            continue
        for g in GENRES:
            sub = df[df["genre"]==g]
            if sub.empty:
                continue
            fig.add_trace(go.Scatter(
                x=sub["x"], y=sub["y"], mode="markers", name=g,
                legendgroup=g, showlegend=(col_idx==1),
                marker=dict(color=GENRE_COLORS.get(g,PALETTE["accent"]),
                            size=5, opacity=.65, line=dict(width=0)),
                hovertemplate=f"<b>{g}</b><extra></extra>",
            ), row=1, col=col_idx)
    fig.update_layout(**base_layout(
        legend=dict(orientation="h",y=-0.12,font=dict(color=PALETTE["muted"],size=10),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=30,r=20,b=70,l=30),
    ))
    for ax in ["xaxis","xaxis2","xaxis3","yaxis","yaxis2","yaxis3"]:
        fig.update_layout(**{ax: dict(gridcolor=PALETTE["border"],zeroline=False,
                                      tickfont=dict(color=PALETTE["muted"],size=8),
                                      showgrid=True)})
    return fig
