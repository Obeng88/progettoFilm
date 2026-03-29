from pydantic import BaseModel, Field
from typing import List, Optional,Dict
from datetime import datetime



class Film(BaseModel):
    Id:int=Field(...,ge=0)
    Titolo: str=Field(...,min_length=1)
    Durata: int=Field(...,gt=0)
    Genere: str=Field(...,min_length=1)
    Regista: str=Field(...,min_length=1)
    Immagine:Optional[str]=Field(default="")
    Descrizione:Optional[str]=Field(default="")


class Sala(BaseModel):
    Id:str=Field(...,min_length=1)      
    PostiTotali: int=Field(...,gt=0)
    PostiDisponibili: int=Field(...,ge=0)


class Spettacolo(BaseModel):
    Id:str=Field(...,min_length=1)
    Film: Film
    Sala: Sala
    Orario: datetime=Field(...)


class posto(BaseModel):
    Fila: str=Field(...,min_length=1)
    numeroPosto: int=Field(...,gt=0)
    Sala: Sala





