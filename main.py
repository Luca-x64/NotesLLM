import os
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from note import Note
from connection import connect_to_db as conn 

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "") # TODO
TIMEOUT_REQUEST = int(os.environ.get("TIMEOUT_REQUEST", 2)) 



app = FastAPI()


class NoteUpdateModel(BaseModel):
    title: str | None
    body: str  | None 

def notfoundException(  note_id: int) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error":"Not Found","message":f"Note with ID {note_id} does not exist."})
def unprocessableEntityException() -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"error":"Unprocessable Entity","message":f"Empty request body. At least one of 'title' or 'body' must be provided."})


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



@app.get("/notes/search/",status_code=status.HTTP_200_OK) # TODO search logic
def search_notes(title: str | None = None, body: str | None = None):
    if (title is None) and (body is None):
        raise unprocessableEntityException()
    return {f"search notes with title {title} and body {body}"} # TODO search notes from database


## LLM API
@app.get("/notes/summarize_body/{note_id}",status_code=status.HTTP_200_OK) # TODO 
async def summarize_body(note_id: int):
    exists = True
    if not exists:
        raise notfoundException(note_id)
    return {f"summarize body of note {note_id}"} # TODO get note from database and call LLM API to summarize body

@app.get("/notes/suggest_title/{note_id}",status_code=status.HTTP_200_OK) # TODO 
async def suggest_title(note_id: int):
    exists = True
    if not exists:
        raise notfoundException(note_id)
    return {f"suggest title of note {note_id}"} # TODO get note from database and call LLM API to suggest title