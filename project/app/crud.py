from sqlalchemy.orm import Session
from . import models, schemas

def create_application(db: Session, app: schemas.ApplicationCreate):
    db_app = models.Application(**app.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

def get_applications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Application).offset(skip).limit(limit).all()
