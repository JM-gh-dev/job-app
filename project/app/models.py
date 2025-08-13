from sqlalchemy import Column, Integer, String
from .database import Base

# Definicja tabeli w bazie
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
