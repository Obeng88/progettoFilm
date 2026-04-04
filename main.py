from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prenotazione(BaseModel):
    film_id: int
    utente_nome: str
    posto: str

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/api/films")
async def get_films():
    conn = sqlite3.connect("moviedb.sqlite")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM film")
    rows = cursor.fetchall()
    conn.close()
    
    films = []
    for r in rows:
        films.append({
            "id": r["Id"],
            "titolo": r["Titolo"],
            "voto": r["Voto"],
            "trama": r["Trama"],
            "sala": r["Sala"],
            "orari": r["Orari"].split(",") if r["Orari"] else [],
            "img": r["Immagine"]
        })
    return films

@app.get("/api/posti-occupati/{film_id}")
async def get_posti(film_id: int):
    conn = sqlite3.connect("moviedb.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT posto FROM prenotazioni WHERE film_id=?", (film_id,))
    posti = [r[0] for r in cursor.fetchall()]
    conn.close()
    return {"occupati": posti}

@app.post("/api/prenota")
async def prenota(dati: Prenotazione):
    conn = sqlite3.connect("moviedb.sqlite")
    cursor = conn.cursor()
    
    # CONTROLLO DI SICUREZZA: Verifica se il posto è già stato preso
    cursor.execute("SELECT id FROM prenotazioni WHERE film_id=? AND posto=?", 
                   (dati.film_id, dati.posto))
    già_prenotato = cursor.fetchone()
    
    if già_prenotato:
        conn.close()
        # Se il posto esiste già, restituiamo un errore 400
        raise HTTPException(status_code=400, detail="Spiacenti, questo posto è già stato occupato!")

    # Se il posto è libero, procediamo con l'inserimento
    try:
        cursor.execute("INSERT INTO prenotazioni (film_id, utente_nome, posto) VALUES (?, ?, ?)",
                       (dati.film_id, dati.utente_nome, dati.posto))
        conn.commit()
        conn.close()
        return {"status": "OK"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Errore del database: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)