from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional,Dict
import requests
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from classi.MovieClasses import Posto,Spettacolo,Sala
import sqlite3
from fastapi.params import Body


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


'''Funzione per convertire i risultati delle sale in un dizionario'''
def to_dict_sala(sala):
    return {
        "Id": sala.Id,
        "PostiTotali": sala.PostiTotali,
        "PostiDisponibili": sala.PostiDisponibili
    }

'''Funzione per ottenere i dettagli di una sala specifica'''
def get_watchroom_by_id(id:int):
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM sala WHERE Idsala=?", (id,))
    sala=cursor.fetchone()
    conn.close()
    s=Sala(Id=sala[0], PostiTotali=sala[1], PostiDisponibili=sala[2])
    return s

'''Funzione per ottenere tutti gli spettacoli disponibili'''
def get_all_shows(id:int):
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM spettacolo")
    spettacoli=cursor.fetchall()
    conn.close()
    return spettacoli

'''Funzione per convertire i risultati degli spettacoli in un dizionario'''
def to_dict_show(spettacoli):
    show_dict={}
    for show in spettacoli:
        show_dict[show[0]]={
            "Film": show[1],
            "Sala": show[2],
            "Orario": show[3]
        }
    return show_dict

'''Funzione per convertire i risultati dei posti in un dizionario'''
def to_dict_seats(posti):
    seat_dict={}
    i=0
    for posto in posti:
        seat_dict[i]={
            "Fila": posto.Fila,
            "NumeroPosto": posto.numeroPosto,
            "Sala": posto.Sala,
            "Stato": posto.stato
        }
        i+=1
    return seat_dict

'''Funzione per ottenere i posti di una sala specifica'''
def get_seats_by_watchroom(id:int):
    seats=[]
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM posto WHERE salaId=?", (id,))
    posti=cursor.fetchall()
    conn.close()
    for posto in posti:
        s=Posto(Fila=posto[0], numeroPosto=posto[1], Sala=posto[2], stato=posto[3])
        seats.append(s)
    return seats

'''Funzione per cercare un posto specifico in una lista di posti'''
def search_seats_in_list(filaNumero:str, sala_id:int):
    seats=get_seats_by_watchroom(sala_id)
    for seat in seats:
        if (seat.Fila+str(seat.numeroPosto))==filaNumero:
            return seat
    return "Posto non trovato"

'''Funzione per aggiornare il numero di posti disponibili in una sala dopo una prenotazione'''
def update_watchroom_seats(sala_id:int, posti_rimanenti:int):
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("UPDATE sala SET postiDisponibili=? WHERE Idsala=?", (posti_rimanenti, sala_id))
    conn.commit()
    conn.close()

'''Funzione per bloccare un posto specifico dopo una prenotazione'''
def block_seat(posto: Posto):
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("UPDATE posto SET stato=1 WHERE Fila=? AND numeroPosto=? AND salaId=?", 
                   (posto.Fila, posto.numeroPosto, posto.Sala))
    conn.commit()
    conn.close()

'''Funzione per aggiungere una prenotazione al database'''
def add_prenotazione(spettacolo_id:int, special_code:str, costo_totale:int, numero_posti:int, posti:str):
    conn=sqlite3.connect("moviedb.sqlite")
    cursor=conn.cursor()
    cursor.execute("INSERT INTO prenota (SpettacoloId, SpecialCode, costoTotale, numeroPostiPrenotati, Posti) VALUES (?, ?, ?, ?, ?)", 
                   (spettacolo_id, special_code, costo_totale, numero_posti, posti))
    conn.commit()
    conn.close()

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

'''Endpoint per ottenere i dettagli di una sala specifica'''
@app.get("/sala/{id}")
async def get_sala(id: int):
    sala=get_watchroom_by_id(id)
    if not sala:
        raise HTTPException(status_code=404, detail="Sala non trovata")
    return to_dict_sala(sala)


'''Endpoint per ottenere tutti gli spettacoli disponibili'''
@app.get("/spettacoli")
async def get_spettacoli():
    spettacoli=get_all_shows(0)
    if len(spettacoli)==0:
        raise HTTPException(status_code=404, detail="Nessuno spettacolo trovato")
    return to_dict_show(spettacoli)

'''Endpoint per ottenere i posti di una sala specifica'''
@app.get("/sala/{id}/posti")
async def get_posti(id: int):
    posti=get_seats_by_watchroom(id)
    if len(posti)==0:
        raise HTTPException(status_code=404, detail="Nessun posto trovato per questa sala o la sala non esiste")
    return to_dict_seats(posti)


'''Endpoint per prenotare un posto/i specifico in uno spettacolo specifico'''
@app.post("/prenota")
async def prenota(prenotazione: dict = Body(...)):
    sala=get_watchroom_by_id(prenotazione["salaId"])
    postiDisponibili=prenotazione["Posti"].split(",")
    postiRimanenti=sala.PostiDisponibili-prenotazione["numeroPostiPrenotati"]

    for posto in postiDisponibili:
        p=search_seats_in_list(posto, sala.Id)
        if p=="Posto non trovato":
            raise HTTPException(status_code=404, detail=f"Il posto {posto.Fila}{posto.numeroPosto} non esiste nella sala {prenotazione['salaId']}")
        else:
            block_seat(p)

    update_watchroom_seats(sala.Id, postiRimanenti)
    add_prenotazione(prenotazione["SpettacoloId"], prenotazione["SpecialCode"], prenotazione["costoTotale"], prenotazione["numeroPostiPrenotati"],prenotazione["Posti"])

    return {"message": "Prenotazione effettuata con successo!"}