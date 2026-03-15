from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import requests
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Film(BaseModel):
    Titolo: str
    Durata: int
    Genere: str
    Regista: str
    Immagine:Optional[str]=""


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],  # in produzione metti il tuo dominio
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return FileResponse("index.html")



fake_db2={
    
}

fake_db={
    "UUID1":{
        "Titolo":"Io sono leggenda",
        "Durata":101,
        "Genere":"Azione",
        "Regista":"Francis Lawrence"
    },
    "UUID2": {
        "Titolo": "The Godfather",
        "Durata": 175,
        "Genere":"Crime",
        "Regista": "Francis Ford Coppola"
    },
    "UUID3": {
        "Titolo": "Pulp Fiction",
        "Durata": 154,
        "Genere":"Crime",
        "Regista": "Quentin Tarantino"
    },
    "UUID4": {
        "Titolo": "Titanic",
        "Durata": 195,
        "Genere": "Romantico",
        "Regista": "James Cameron"
    },
    "UUID5": {
        "Titolo": "The Dark Knight",
        "Durata": 152,
        "Genere": "Azione",
        "Regista": "Christopher Nolan"
    },
    "UUID6": {
        "Titolo": "The Shawshank Redemption",
        "Durata": 142,
        "Genere": "Drammatico",
        "Regista": "Frank Darabont"
    },
    "UUID7": {
        "Titolo": "Fight Club",
        "Durata": 139,
        "Genere": "Thriller",
        "Regista": "David Fincher"
    },
    "UUID8": {
        "Titolo": "Forrest Gump",
        "Durata": 142,
        "Genere": "Drammatico",
        "Regista": "Robert Zemeckis"
    },
    "UUID9": {
        "Titolo": "Interstellar",
        "Durata": 169,
        "Genere": "Fantascienza",
        "Regista": "Christopher Nolan"
    },
    "UUID10": {
        "Titolo": "Gladiator",
        "Durata": 155,
        "Genere": "Storico",
        "Regista": "Ridley Scott"
    },
    "UUID11":{
        "Titolo": "Se7en",
        "Durata": 127,
        "Genere": "Thriller",
        "Regista": "David Fincher"
    },
    "UUID12":{
        "Titolo": "Shrek",
        "Durata": 89,
        "Genere": "Commedia",
        "Regista": "Vicky Jenson"
    },
    "UUID13":{
        "Titolo": "The Mask:da zero a mito",
        "Durata": 97,
        "Genere": "Commedia",
        "Regista": "Chuck Russell"
    }

}

@app.get("/films")
async def get_all_movies():
    return fake_db

@app.get("/film/genre/{genre}")
async def get_all_movies_genre(genre:str):
    temp=fake_db.copy()
    for filmK in list(temp.keys()):
        if temp[filmK]["Genere"].lower()!=genre:
            temp.pop(filmK)
    
    if len(temp)==0:
        raise HTTPException(status_code=404, detail="Nessun film trovato per questo genere")

    return temp        


@app.get("/film/{id}")
async def get_movie(id:str):
    if id.upper() not in fake_db:
        raise HTTPException(status_code=404, detail="Film non trovato")
    return fake_db[id.upper()]


@app.get("/films/director/{director}")
async def get_director_films(director:str):
    d=director.replace("-", " ")
    temp=fake_db.copy()
    for filmK in list(temp.keys()):
        if temp[filmK]["Regista"].lower()!=d.lower():
            temp.pop(filmK)
    
    if len(temp)==0:
        raise HTTPException(status_code=404, detail="Nessun regista trovato.")

    return temp

@app.get("/films/genres")
async def get_unique_genres():

    temp=fake_db.copy()
    generi=[]
    duplicates=[]                                                         
    dbkeys=list(temp.keys())
    for k in dbkeys:
        duplicates.append(temp[k]["Genere"])
    for key in dbkeys:
        if temp[key]["Genere"] not in generi:
            generi.append(temp[key]["Genere"])

    return generi
