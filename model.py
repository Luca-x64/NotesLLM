from pydantic import BaseModel
from datetime import date as Date

class NoteUpdateModel(BaseModel):
    title: str | None
    body: str  | None 

class NoteSearchModel(BaseModel):
    title: str | None = None
    date: Date | None = None
    first_date: Date | None = None
    second_date: Date | None = None