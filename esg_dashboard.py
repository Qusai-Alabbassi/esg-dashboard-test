#!/usr/bin/env python
# coding: utf-8

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import base64
import os

# Load data
excel_path = "ESG_KPI_Dataset.xlsx"
logo_path = "Bank_of_Jordan_logo.png"
kpi_data = pd.read_excel(excel_path)
kpi_data.dropna(inplace=True)
kpi_data["Year"] = kpi_data["Year"].astype(int)

# Prepare KPI structure
df_kpis = kpi_data[["Pillar", "Category", "KPI"]].drop_duplicates()
pillar_order = ["Environment", "Social", "Governance"]
df_kpis["Pillar"] = pd.Categorical(df_kpis["Pillar"], categories=pillar_order, ordered=True)

# Encode logo
encoded_image = base64.b64encode(open(logo_path, 'rb').read()).decode()

# App setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Bank of Jordan - ESG Dashboard"

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Img(src='data:image/png;base64,{}'.format(encoded_image),
                         style={'height': '60px'}), width="auto"),
        dbc.Col(html.H2("Bank of Jordan – ESG Dashboard",
                        className="text-center text-primary"),
                className="d-flex align-items-center justify-content-center")
    ], justify="between", className="my-3"),

    dbc.Row([
        dbc.Col([
            html.Label("Select ESG Pillar"),
            dcc.Dropdown(
                id="pillar-dropdown",
                options=[{"label": p, "value": p} for p in pillar_order],
                value="Environment"
            )
        ], md=4),
        dbc.Col([
            html.Label("Select Category"),
            dcc.Dropdown(id="category-dropdown")
        ], md=4),
        dbc.Col([
            html.Label("Select KPI"),
            dcc.Dropdown(
                id="kpi-dropdown",
                style={"whiteSpace": "normal"},
                optionHeight=50
            )
        ], md=4),
    ], className="mb-3"),

    dbc.Card([
        dbc.CardBody([
            dcc.Graph(id="kpi-graph", config={"displayModeBar": False})
        ])
    ], className="shadow-sm"),

    html.Div("Dashboard designed and coded by Qusai Alabbassi © 2025",
             className="text-center text-muted mt-4")
], fluid=True)

# Callbacks
@app.callback(
    Output("category-dropdown", "options"),
    Output("category-dropdown", "value"),
    Input("pillar-dropdown", "value")
)
def update_category_options(pillar):
    categories = df_kpis[df_kpis["Pillar"] == pillar]["Category"].unique()
    return [{"label": c, "value": c} for c in categories], categories[0] if len(categories) > 0 else None

@app.callback(
    Output("kpi-dropdown", "options"),
    Output("kpi-dropdown", "value"),
    Input("category-dropdown", "value"),
    State("pillar-dropdown", "value")
)
def update_kpi_options(category, pillar):
    kpis = df_kpis[
        (df_kpis["Pillar"] == pillar) &
        (df_kpis["Category"] == category)
    ]["KPI"].unique()
    return [{"label": k, "value": k} for k in kpis], kpis[0] if len(kpis) > 0 else None

@app.callback(
    Output("kpi-graph", "figure"),
    Input("pillar-dropdown", "value"),
    Input("category-dropdown", "value"),
    Input("kpi-dropdown", "value")
)
def update_kpi_graph(pillar, category, kpi):
    filtered_df = kpi_data[
        (kpi_data["Pillar"] == pillar) &
        (kpi_data["Category"] == category) &
        (kpi_data["KPI"] == kpi)
    ]
    y_axis_title = kpi.split("(")[-1].replace(")", "").strip() if "(" in kpi else "Value"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered_df["Year"],
        y=filtered_df["Value"],
        mode="lines+markers",
        line=dict(color="black"),
        marker=dict(size=8),
        name=kpi
    ))

    fig.update_layout(
        height=500,
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(dtick=1, title="Year"),
        yaxis=dict(title=y_axis_title),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )

    return fig

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)
