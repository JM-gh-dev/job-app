from sqlalchemy import Column, Integer, String, Date, Numeric
from .database import Base

# Definicja tabeli w bazie
class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    firma = Column(String, index=True)
    stanowisko = Column(String)
    link = Column(String)
    link2 = Column(String, nullable=True)
    widełki_min = Column(Numeric, nullable=True)
    widełki_max = Column(Numeric, nullable=True)
    rodzaj_umowy = Column(String)
    data_zlozenia = Column(Date)
    odpowiedz = Column(String)
    description = Column(String, nullable=True)
