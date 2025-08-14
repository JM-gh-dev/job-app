from sqlalchemy import Column, Integer, String, Date, Numeric
from .database import Base

# Definicja tabeli w bazie
class Application(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    firma = Column(String, index=True)
    stanowisko = Column(String)
    link = Column(String)
    widełki_min = Column(Numeric)
    widełki_max = Column(Numeric)
    rodzaj_umowy = Column(String)
    data_zlozenia = Column(Date)
    odpowiedz = Column(String)
    desc = Column(String)
