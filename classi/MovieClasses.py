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
    Id:int=Field(...,ge=0)      
    PostiTotali: int=Field(...,gt=0)
    PostiDisponibili: int=Field(...,ge=0)


class Spettacolo(BaseModel):
    Id:int=Field(...,ge=0)
    Film: int=Field(...,ge=0)
    Sala: int=Field(...,ge=0)
    Orario: str=Field(...)



class Posto(BaseModel):
    Fila: str=Field(...,min_length=1)
    numeroPosto: int=Field(...,gt=0)
    Sala: int=Field(...,ge=0)
    stato:int=Field(...,ge=0,le=1) # 0 libero, 1 occupato





