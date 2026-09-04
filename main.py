import os
from fastapi import FastAPI,status
from contextlib import asynccontextmanager
from model import NoteSearchModel, NoteUpdateModel
from connection import connect_to_db as conn 
from connection import create_db
from utility import notfoundException, unprocessableEntityException, parse_date

import requests

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
TIMEOUT_REQUEST = int(os.environ.get("TIMEOUT_REQUEST", 10)) 


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
def get_note(skip: int = 0, limit: int = 20):
    with conn() as con:
        cur = con.cursor()
        query = f"SELECT * FROM notes LIMIT ? OFFSET ?"
        cur.execute(query, (limit, skip))

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

def ask_model(system_prompt: str, user_prompt: str):
    payload = {
    "model": OLLAMA_MODEL,
    "stream": False,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]}
    response = requests.post(OLLAMA_BASE_URL + "/api/chat", json=payload, timeout=TIMEOUT_REQUEST)
    print(response.status_code) #DEBUG
    print(response.text) # DEBUG
    return response.json()["message"]["content"] 

## LLM API
@app.get("/notes/summarize_body/{note_id}",status_code=status.HTTP_200_OK) 
async def summarize_body(note_id: int):
    body = get_notebody_by_id(note_id)
    response = ask_model("Sei un assistente che riassume testi in italiano", "genera un riassunto di circa due righe, rispondi solo con il riassunto: "+ body)
    return {f"{response}"}

@app.get("/notes/suggest_title/{note_id}",status_code=status.HTTP_200_OK) # TODO 
async def suggest_title(note_id: int):
    body = get_notebody_by_id(note_id)
    #response = ask_model("Sei un assistente italiano,che propone un titolo breve e coerente dato un testo", body)
    
    return {f"suggest title of note {note_id}: with body: {body}"} # TODO g call LLM API to suggest title