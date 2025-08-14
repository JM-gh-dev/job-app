# app/dashboard.py
import dash
from dash import dcc, html, Output, Input
import plotly.express as px
import pandas as pd
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models

# Dash będzie dostępny pod /dash/
dash_app = dash.Dash(__name__, requests_pathname_prefix="/dash/")

def load_df():
    """Pobierz daty złożenia aplikacji z bazy i policz ile było danego dnia."""
    db: Session = SessionLocal()
    try:
        rows = db.query(models.Application.data_zlozenia).all()  # [(date,), (date,), ...]
    finally:
        db.close()

    df = pd.DataFrame(rows, columns=["data_zlozenia"]).dropna()
    if df.empty:
        return df

    # upewniamy się, że to kolumna typu datetime i sortujemy
    df["data_zlozenia"] = pd.to_datetime(df["data_zlozenia"])
    grouped = df.value_counts("data_zlozenia").sort_index().rename("liczba").reset_index()
    return grouped  # kolumny: data_zlozenia, liczba

def load_contract_df():
    """Pobiera rodzaje umów i zlicza ile jest każdego typu."""
    db: Session = SessionLocal()
    try:
        rows = db.query(models.Application.rodzaj_umowy).all()
    finally:
        db.close()

    df = pd.DataFrame(rows, columns=["rodzaj_umowy"]).dropna()
    if df.empty:
        return df

    grouped = df.value_counts("rodzaj_umowy").rename("liczba").reset_index()
    return grouped  # kolumny: rodzaj_umowy, liczba

dash_app.layout = html.Div(
    [
        html.H2("Liczba aplikacji w czasie"),
        dcc.Graph(id="applications-time"),

        html.H2("Udział rodzajów umów"),
        dcc.Graph(id="contracts-pie"),

        dcc.Interval(id="tick", interval=5_000, n_intervals=0),  # auto-refresh co 5s
    ],
    style={"maxWidth": "900px", "margin": "0 auto", "padding": "16px"},
)

# ---- Callback dla pierwszego wykresu ----
@dash_app.callback(
        Output("applications-time", "figure"),
        Input("tick", "n_intervals")
)
def update_chart(_):
    df = load_df()
    if df.empty:
        return px.line(title="Brak danych (dodaj rekord w /docs → POST /applications/)")

    fig = px.line(
        df, x="data_zlozenia", y="liczba", markers=True, title="Liczba aplikacji dziennie"
    )
    fig.update_layout(xaxis_title="Data", yaxis_title="Liczba aplikacji")
    return fig

# ---- Callback dla drugiego wykresu ----
@dash_app.callback(
        Output("contracts-pie", "figure"),
        Input("tick", "n_intervals")
)
def update_pie(_):
    df = load_contract_df()
    if df.empty:
        return px.pie(title="Brak danych (dodaj rekordy z rodzajem umowy)")

    fig = px.pie(df, names="rodzaj_umowy", values="liczba", title="Udział rodzajów umów")
    fig.update_traces(textinfo="percent+label")
    return fig