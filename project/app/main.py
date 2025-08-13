from fastapi import FastAPI
from . import models
from .database import engine

# Tworzymy tabelę, jeśli jej nie ma
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Działa!"}
