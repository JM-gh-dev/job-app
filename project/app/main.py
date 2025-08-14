from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
from starlette.middleware.wsgi import WSGIMiddleware
from .dashboard import dash_app

# Tworzymy tabelę, jeśli jej nie ma
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#@app.get("/")
#def home():
#    return {"message": "Działa!"}

@app.post("/applications/", response_model=schemas.Application)
def create_application(app_data: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    return crud.create_application(db, app_data)

@app.get("/applications/", response_model=list[schemas.Application])
def read_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_applications(db, skip=skip, limit=limit)

# Podpinamy Dash pod FastAPI
app.mount("/dash", WSGIMiddleware(dash_app.server))
