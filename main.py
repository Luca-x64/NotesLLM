import os
from fastapi import FastAPI,status
from contextlib import asynccontextmanager
from model import NoteSearchModel, NoteUpdateModel
from connection import connect_to_db as conn 
from connection import create_db
from utility import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield

app = FastAPI(lifespan=lifespan)



@app.get("/notes/{note_id}",status_code=status.HTTP_200_OK)  
def get_note(note_id: int):
    with conn() as con:
        cur = con.cursor()
        query = "SELECT * FROM notes WHERE id = ?"
        cur.execute(query, (note_id,))
        note = cur.fetchone()

    if note is None:
        raise notfoundException(note_id)
    return note

@app.get("/notes",status_code=status.HTTP_200_OK)    
def get_note(limit: int = 20):
    with conn() as con:
        cur = con.cursor()
        query = f"SELECT * FROM notes LIMIT ?"
        cur.execute(query, (limit,))

        return cur.fetchall()

@app.post("/notes/edit/{note_id}",status_code=status.HTTP_200_OK)
async def edit_note(note_id:int, note_update: NoteUpdateModel):
    if (note_update.title is None) and (note_update.body is None): # CHECK maybe not needed for pydantic validation
            raise unprocessableEntityException()

    
    with conn() as con:
        cur = con.cursor()
        query = """UPDATE NOTES SET 
                    title = COALESCE(?, title), 
                    body = COALESCE(?, body) 
                    WHERE id = ?"""
        cur.execute(query, (note_update.title, note_update.body, note_id))
        updated_rows = cur.rowcount

        if updated_rows == 0:
            raise notfoundException(note_id)
        
        con.commit()

    

@app.post("/notes/create",status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteUpdateModel):
    if (note.title is None) and (note.body is None):
            raise unprocessableEntityException()
    with conn() as con:
        cur = con.cursor()

        query = f"INSERT INTO notes (title, body) VALUES (?, ?)"
        cur.execute(query, (note.title, note.body))
        

@app.delete("/notes/delete/{note_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int):
    with conn() as con:
        cur = con.cursor()
        query = "DELETE FROM notes WHERE id = ?"
        cur.execute(query, (note_id,))
        deleted_rows = cur.rowcount
        con.commit()

    if deleted_rows == 0:
        raise notfoundException(note_id)




@app.post("/notes/search/",status_code=status.HTTP_200_OK) 
def search_notes(searchparams: NoteSearchModel):
    title = searchparams.title
    date = searchparams.date
    fd = searchparams.first_date
    sd = searchparams.second_date

    if (title is None) and (date is None) and (fd is None) and (sd is None): # TODO check if fd is present and sd is not present or vice versa, then raise exception, then check if fd is greater than sd, then raise exception 
        raise unprocessableEntityException()
    
    with conn() as con:
        cur = con.cursor()
        query = """SELECT * FROM notes
                   WHERE (? IS NULL OR title LIKE ?)
                     AND (? IS NULL OR date(date) = date(?))
                     AND (? IS NULL OR ? IS NULL
                     OR date(date) BETWEEN date(?) AND date(?))"""
        
        newtitle = f"%{title}%" if title is not None else None
        exact_date = parse_date(date)
        first_date = parse_date(fd)
        second_date = parse_date(sd)

        cur.execute(query, (newtitle, newtitle, 
                            exact_date, exact_date,
                            first_date,second_date,
                            first_date, second_date))
        notes = cur.fetchall()

    return notes

def get_notebody_by_id(note_id: int):
    with conn() as con:
        cur = con.cursor()  
        query = "SELECT body FROM notes WHERE id = ?"
        cur.execute(query, (note_id,))
        note = cur.fetchone()

    if note is None:
        raise notfoundException(note_id)
    return note[0]


## LLM API
@app.get("/notes/summarize_body/{note_id}",status_code=status.HTTP_200_OK) 
async def summarize_body(note_id: int):
    body = get_notebody_by_id(note_id)
    response = ask_model("Sei un assistente che riassume testi in italiano, generando riassunti brevi e coerenti, basati solo sul contenuto del testo, non aggiungere parole che non fanno riferimento al riassunto. Il riassunto è di circa due righe", body)
    return response

@app.get("/notes/suggest_title/{note_id}",status_code=status.HTTP_200_OK)
async def suggest_title(note_id: int):
    body = get_notebody_by_id(note_id)
    response = ask_model('Sei un assistente che propone titoli brevi e coerenti per testi in italiano, basati solo sul contenuto del testo, non aggiungere parole che non fanno riferimento al titolo. non inserire alcun testo extra (tipo "Titolo:""), solo il titolo proposto. Non inserire caratteri speciali, tipo escape sequences', body)
    return response