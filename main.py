from fastapi import FastAPI,status
from contextlib import asynccontextmanager
from model import NoteCreateModel, NoteSearchModel, NoteUpdateModel
from connection import fetch_one, fetch_all, execute
from connection import create_db
from utility import (not_found_exception, ask_model, date_to_iso)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/note/{note_id}",status_code=status.HTTP_200_OK)  
def get_note(note_id: int):
    note = fetch_one("SELECT * FROM notes WHERE id = ?", (note_id,))
    if note is None: raise not_found_exception(note_id)
    return note


@app.get("/notes",status_code=status.HTTP_200_OK)    
def get_notes(limit: int = 20):
    return fetch_all("SELECT id, title, date FROM notes LIMIT ?", (limit,))

@app.post("/notes/edit/{note_id}",status_code=status.HTTP_200_OK)
def edit_note(note_id:int, note_update: NoteUpdateModel):

    updated_rows = execute("""UPDATE NOTES SET 
                title = COALESCE(?, title), 
                body = COALESCE(?, body) 
                WHERE id = ?""", (note_update.title, note_update.body, note_id))

    if updated_rows == 0: raise not_found_exception(note_id)


@app.post("/notes/create",status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreateModel):
    execute("INSERT INTO notes (title, body) VALUES (?, ?)", (note.title, note.body))
        

@app.delete("/notes/delete/{note_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    deleted_rows = execute("DELETE FROM notes WHERE id = ?", (note_id,))
    if deleted_rows == 0: raise not_found_exception(note_id)


@app.post("/notes/search/",status_code=status.HTTP_200_OK) 
def search_notes(searchparams: NoteSearchModel):
    title = f"%{searchparams.title}%" if searchparams.title is not None else None
    date = date_to_iso(searchparams.date)
    fd = date_to_iso(searchparams.first_date)
    sd = date_to_iso(searchparams.second_date)

    query = """SELECT * FROM notes
                   WHERE (? IS NULL OR title LIKE ?)
                     AND (? IS NULL OR date(date) = date(?))
                     AND (? IS NULL OR ? IS NULL
                     OR date(date) BETWEEN date(?) AND date(?))"""
    params = (title, title, date, date, fd, sd, fd, sd)
    notes = fetch_all(query,params)

    return notes


def get_notebody_by_id(note_id: int):
    note = fetch_one("SELECT body FROM notes WHERE id = ?", (note_id,))

    if note is None: raise not_found_exception(note_id)
    return note[0]


## LLM API
@app.get("/notes/summarize_body/{note_id}",status_code=status.HTTP_200_OK) 
def summarize_body(note_id: int):
    body = get_notebody_by_id(note_id)
    response = ask_model("Sei un assistente che riassume testi in italiano, generando riassunti brevi e coerenti, basati solo sul contenuto del testo, non aggiungere parole che non fanno riferimento al riassunto. Il riassunto è di circa due righe",
                          body)
    return response


@app.get("/notes/suggest_title/{note_id}",status_code=status.HTTP_200_OK)
def suggest_title(note_id: int):
    body = get_notebody_by_id(note_id)
    response = ask_model('Sei un assistente che propone titoli brevi e coerenti per testi in italiano, basati solo sul contenuto del testo, non aggiungere parole che non fanno riferimento al titolo. non inserire alcun testo extra (tipo "Titolo:""), solo il titolo proposto. Non inserire caratteri speciali, tipo escape sequences come (", \\)',
                          body)
    return response