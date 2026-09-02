import os
from fastapi import FastAPI, HTTPException, Response, status

from note import Note

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "") # TODO
DBPATH = os.environ.get("DBPATH", "") # TODO
TIMEOUT_REQUEST = int(os.environ.get("TIMEOUT_REQUEST", 2)) 



app = FastAPI()


from pydantic import BaseModel

class NoteUpdateModel(BaseModel):
    title: str | None
    body: str  | None 

def notfoundException(  note_id: int) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error":"Not Found","message":f"Note with ID {note_id} does not exist."})



@app.get("/notes/{note_id}",status_code=status.HTTP_200_OK)  
def get_note(note_id: int):
    exists = True
    if not exists:
        raise notfoundException(note_id)
    return {f"note {note_id}"} # TODO get note from database

@app.get("/notes",status_code=status.HTTP_200_OK)    
def get_note(skip: int = 0, limit: int = 20):
    return {f"all notes"} # TODO get all notes from database


@app.post("/notes/edit/{note_id}",status_code=status.HTTP_200_OK) # TODO update on DB
async def edit_note(node_id:int, note_update: NoteUpdateModel):
    exists = True
    if not exists:
        raise notfoundException(node_id)

    if (note_update.title is None) and (note_update.body is None):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"error":"Unprocessable Entity","message":f"Empty request body. At least one of 'title' or 'body' must be provided."})

@app.post("/notes/create",status_code=status.HTTP_201_CREATED) # TODO insert note into database
async def create_note(note: NoteUpdateModel):
    return note 

@app.delete("/notes/delete/{note_id}",status_code=status.HTTP_204_NO_CONTENT) # TODO delete note from database
async def delete_note(note_id: int):
    success = True
    id_not_found = True
    if id_not_found:
        raise notfoundException(note_id)

# TODO:



#@app.get("/notes/search",status_code=status.HTTP_200_OK) # TODO search logic



