from pydantic import BaseModel
from typing import List, Optional,Dict



class Film(BaseModel):
    Id:str
    Titolo: str
    Durata: int
    Genere: str
    Regista: str
    Immagine:Optional[str]=""


class Sala(BaseModel):
    Id:str
    PostiTotali: int
    PostiDisponibili: int


class Spettacolo(BaseModel):
    Id:str
    Film: Film
    Sala: Sala
    Orario: str




