from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import date as Date

class NoteCreateModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace = True) 

    title: str = Field(min_length=1,description="Title of the note")
    body: str = Field(max_length=3000,description="Body of the note")

class NoteUpdateModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace = True)
    title: str | None = Field(default=None,min_length=1,description="Title of the note")
    body: str  | None = Field(default=None, max_length=3000,description="Body of the note")

    @model_validator(mode="after")
    def validate_empty_request(self):
        if self.title is None and self.body is None:
            raise ValueError("At least one field between title and body must be provided")
        return self

class NoteSearchModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=1)
    date: Date | None = None
    first_date: Date | None = None
    second_date: Date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if all(v is None for v in [self.title,self.date, self.first_date, self.second_date]):
            raise ValueError("All fields are None.")

        if (self.first_date is None) != (self.second_date is None):
            raise ValueError("Both first_date and second_date must be provided together.")
        if (self.first_date is not None
            and self.second_date is not None
            and self.first_date > self.second_date):
            raise ValueError("first_date cannot be greater than second_date")
        return self