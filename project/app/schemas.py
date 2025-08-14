from pydantic import BaseModel
from datetime import date
from typing import Optional

class ApplicationBase(BaseModel):
    firma: str
    stanowisko: str
    link: Optional[str] = None
    widełki_min: Optional[float] = None
    widełki_max: Optional[float] = None
    rodzaj_umowy: Optional[str] = None
    data_zlozenia: Optional[date] = None
    odpowiedz: Optional[str] = None
    desc: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class Application(ApplicationBase):
    id: int

    class Config:
        orm_mode = True
