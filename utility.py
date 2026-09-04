from fastapi import HTTPException,status


def notfoundException(  note_id: int) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error":"Not Found","message":f"Note with ID {note_id} does not exist."})
def unprocessableEntityException() -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"error":"Unprocessable Entity","message":f"Empty request body. At least one of 'title' or 'body' must be provided."})


def parse_date(date):
    return date.isoformat() if date is not None else None

