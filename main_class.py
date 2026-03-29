from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional,Dict
import requests
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import classi.MovieClasses as MovieClasses
import sqlite3


app=FastAPI()

'''Configurazione CORS per permettere al frontend di comunicare con il backend'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],  # in produzione metti il tuo dominio
    allow_methods=["*"],
    allow_headers=["*"],
)

'''Funzioni per interagire con il database'''
def connect_db():
    conn=sqlite3.connect("moviedb.sqlite")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

def get_films_db():
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM film")
    films=cursor.fetchall()
    conn.close()
    return films

def get_film_by_genre(genre:str):
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM film WHERE Genere=?", (genre.capitalize(),))
    films=cursor.fetchall()
    conn.close()
    return films

def get_film_by_id(id:int):
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM film WHERE Id=?", (id,))
    film=cursor.fetchone()
    conn.close()
    return film

def get_film_by_director(director:str):
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM film WHERE Regista LIKE ?", (director,))
    films=cursor.fetchall()
    conn.close()
    return films

def get_all_genres():
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("SELECT DISTINCT Genere FROM film")
    genres=cursor.fetchall()
    conn.close()
    return [genre[0] for genre in genres]


'''Funzione per convertire i risultati del database in un dizionario'''
def to_dict(films):
    film_dict={}
    for film in films:
        film_dict[film[0]]={
            "Titolo": film[1],
            "Durata": film[2],
            "Genere": film[3],
            "Regista": film[4],
            "Immagine": film[5],
            "Descrizione": film[6]
        }
    return film_dict

'''Endpoint per servire l'index.html''' 
@app.get("/")
async def root():
    return FileResponse("index.html")

'''Endpoint per ottenere tutti i film'''
@app.get("/films")
async def get_all_movies():
    return to_dict(get_films_db())

'''Endpoint per ottenere i film di un genere specifico'''
@app.get("/film/genre/{genre}")
async def get_all_movies_genre(genre:str):
    films=get_film_by_genre(genre)
    if len(films)==0:
        raise HTTPException(status_code=404, detail="Nessun film trovato per questo genere")
    return to_dict(films)

'''Endpoint per ottenere i dettagli di un film specifico'''
@app.get("/film/{id}")
async def get_movie(id: int):
    film=get_film_by_id(id)
    if not film:
        raise HTTPException(status_code=404, detail="Film non trovato")
    return to_dict([film])

'''Endpoint per ottenere i film di un regista specifico'''
@app.get("/films/director/{director}")
async def get_director_films(director:str):
    d=director.replace("-", " ")
    films=get_film_by_director(d)
    if len(films)==0:
        raise HTTPException(status_code=404, detail="Nessun regista trovato.")
    return to_dict(films)

'''Endpoint per ottenere tutti i generi disponibili'''
@app.get("/films/genres")
async def get_unique_genres():
    return get_all_genres()
