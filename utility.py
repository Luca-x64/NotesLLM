import os
from fastapi import HTTPException,status
import requests

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
TIMEOUT_REQUEST = int(os.environ.get("TIMEOUT_REQUEST", 30)) 
OLLAMA_API_RELATIVE_URL = os.environ.get("OLLAMA_API_RELATIVE_URL", "/api/chat")

def notfoundException(  note_id: int) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error":"Not Found","message":f"Note with ID {note_id} does not exist."})
def unprocessableEntityException() -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"error":"Unprocessable Entity","message":f"Empty request body. At least one of 'title' or 'body' must be provided."})

def llm_request(url, payload, timeout):
    try:
        response = requests.post(url, json=payload, timeout=timeout)

    except requests.Timeout:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail={"error":"Ollama Timeout","message":"Request to Ollama API timed out."})
                
    except requests.ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail={"error":"Ollama Connection Error","message":f"Failed to connect to Ollama API. {e}"}) 
                           
    except requests.RequestException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"error":"Ollama not Available","message":f"Failed to communicate with Ollama: {e}"})

    if  response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"error":"Model not Available","message":f"Model: {OLLAMA_MODEL} is not available or installed."})
       
    try:
        content =  response.json()["message"]["content"] 
    except requests.exceptions.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail={"error":"Invalid Response","message":f"Failed to decode JSON response from Ollama API: {e}"})
    
    
    if content.strip() == "":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error":"Empty Response","message":"Ollama API returned an empty response."})

    return content

def ask_model(system_prompt: str, user_prompt: str):
    payload = {
    "model": OLLAMA_MODEL,
    "stream": False,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]}
    content = llm_request(OLLAMA_BASE_URL + OLLAMA_API_RELATIVE_URL, payload, TIMEOUT_REQUEST)
    return content

def parse_date(date):
    return date.isoformat() if date is not None else None

