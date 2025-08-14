# app/dashboard.py
import dash
from dash import dcc, html, Output, Input, dash_table
import plotly.express as px
import pandas as pd
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models

# Dash będzie dostępny pod /dash/
dash_app = dash.Dash(__name__, requests_pathname_prefix="/dash/")

def load_table_df():
    """Ładuje wszystkie aplikacje z bazy jako DataFrame."""
    db: Session = SessionLocal()
    try:
        rows = db.query(models.Application).all()
    finally:
        db.close()

    # Konwertujemy obiekty SQLAlchemy na słowniki
    data = [
        {
            "nazwa_firmy": r.firma,
            "stanowisko": r.stanowisko,
            "link": r.link,
            "link2": r.link2,
            "widełki_min": r.widełki_min,
            "widełki_max": r.widełki_max,
            "rodzaj_umowy": r.rodzaj_umowy,
            "data_zlozenia": r.data_zlozenia,
            "odpowiedz": r.odpowiedz,
            "description": r.description
        }
        for r in rows
    ]
    return pd.DataFrame(data)


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

def load_salary_df():
    """Liczy średnią wartość widełek (średnia z min i max) w podziale na rodzaj umowy."""
    db: Session = SessionLocal()
    try:
        rows = db.query(
            models.Application.rodzaj_umowy,
            models.Application.widełki_min,
            models.Application.widełki_max
        ).all()
    finally:
        db.close()

    df = pd.DataFrame(rows, columns=["rodzaj_umowy", "min", "max"]).dropna()
    if df.empty:
        return df

    # Średnia dla każdego rekordu
    df["średnia"] = (df["min"] + df["max"]) / 2

    # Grupujemy po rodzaju umowy i liczymy średnią z tych średnich
    grouped = df.groupby("rodzaj_umowy", as_index=False)["średnia"].mean()
    return grouped


df = load_table_df()
apps_count = df.shape[0]  # liczba rekordów

dash_app.layout = html.Div(
    [
        html.H1("Panel rekrutacyjny", style={"textAlign": "center"}),

        # ---- TABELA ----
        html.H3(f"Lista aplikacji ({apps_count})"),
        dash_table.DataTable(
            id="applications-table",
            columns=[
                {"name": "Nazwa firmy", "id": "nazwa_firmy"},
                {"name": "Stanowisko", "id": "stanowisko"},
                {"name": "Link", "id": "link"},
                {"name": "Link 2", "id": "link2"},
                {"name": "Widełki min", "id": "widełki_min"},
                {"name": "Widełki max", "id": "widełki_max"},
                {"name": "Rodzaj umowy", "id": "rodzaj_umowy"},
                {"name": "Data złożenia", "id": "data_zlozenia"},
                {"name": "Odpowiedź", "id": "odpowiedz"},
                {"name": "Opis", "id": "description"},
            ],
            data=[],
            page_size=5,
            style_table={
                #"overflowX": "auto",
                "width": "100%",
                #"minWidth": "100%",
                "margin": "0",
            },
            style_cell={
                "textAlign": "left",
                "padding": "5px",
                "whiteSpace": "normal",
                "height": "auto",
                "minWidth": "100px",
                "width": "auto",
                "maxWidth": "none"
            },
            style_header={
                "backgroundColor": "lightgrey",
                "fontWeight": "bold"
            }
        ),

        html.Hr(style={"maxWidth": "100%", "margin": "0","justifyContent": "center"}
),

        # FILTRY
        html.Div([
            html.Div([
                html.Label("Zakres dat:"),
                dcc.DatePickerRange(
                    id="date-range",
                    display_format="YYYY-MM-DD"
                ),
            ], style={"marginRight": "40px"}),

            html.Div([
                html.Label("Rodzaj umowy:"),
                dcc.Dropdown(
                    id="contract-filter",
                    multi=True,
                    placeholder="Wybierz rodzaj umowy"
                ),
            ], style={"flex": 1}),
        ], style={"display": "flex", "marginBottom": "40px"}),

        # RZĄD 1 — wykres czasu i wykres kołowy
        html.Div([
            html.Div([
                html.H3("Aplikacje w czasie"),
                dcc.Graph(id="applications-time", style={"height": "400px"})
            ], style={"flex": 1, "marginRight": "20px"}),

            html.Div([
                html.H3("Rodzaje umów"),
                dcc.Graph(id="contracts-pie", style={"height": "400px"})
            ], style={"flex": 1}),
        ], style={"display": "flex", "marginBottom": "40px"}),

        # RZĄD 2 — wykres płac
        html.Div([
            html.Div([
                html.H3("Średnie widełki płacowe"),
                dcc.Graph(id="salary-bar", style={"height": "400px"})
            ], style={"flex": 1}),
        ], style={"display": "flex"}),

        dcc.Interval(id="tick", interval=5_000, n_intervals=0),
    ],
    style={"maxWidth": "100%", "maxWidth": "100%", "margin": "0", "padding": "0"},
)

# ---- Callback dla tabeli ----
@dash_app.callback(
    Output("applications-table", "data"),
    Input("tick", "n_intervals")
)
def update_table(_):
    df = load_table_df()
    return df.to_dict("records")

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

# ---- Callback dla trzeciego wykresu ----
@dash_app.callback(
    Output("salary-bar", "figure"),
    Input("tick", "n_intervals")
)
def update_salary_chart(_):
    df = load_salary_df()
    if df.empty:
        return px.bar(title="Brak danych (uzupełnij widełki w rekordach)")

    fig = px.bar(
        df,
        x="rodzaj_umowy",
        y="średnia",
        title="Średnie widełki płacowe wg rodzaju umowy",
        text_auto=".2f"
    )
    fig.update_layout(xaxis_title="Rodzaj umowy", yaxis_title="Średnia płaca")
    return fig




