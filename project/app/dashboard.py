import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models

# Tworzymy Dash app
dash_app = dash.Dash(__name__, requests_pathname_prefix="/dash/")

# Funkcja pobierająca dane z bazy
def load_data():
    db: Session = SessionLocal()
    items = db.query(models.Item).all()
    db.close()
    return pd.DataFrame([{"id": item.id, "name": item.name} for item in items])

# Layout – to, co widzimy w przeglądarce
dash_app.layout = html.Div([
    html.H1("Wykres przedmiotów"),
    dcc.Graph(id="items-graph")
])

# Callback – co się dzieje przy załadowaniu strony
@dash_app.callback(
    dash.Output("items-graph", "figure"),
    dash.Input("items-graph", "id")
)
def update_graph(_):
    df = load_data()
    if df.empty:
        fig = px.scatter(title="Brak danych w bazie")
    else:
        fig = px.bar(df, x="id", y="name", title="Lista przedmiotów")
    return fig
