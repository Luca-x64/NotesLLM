# NotesLLM


### TODO
- search api validation date consistency
- pydantic validation
    - il titolo è obbligatorio;
    - il titolo non può essere vuoto;
    - il titolo non può essere composto solamente da spazi;
    - il corpo non può superare i 3.000 caratteri;
    - la data non può essere fornita o modificata dall’utente;
    - non è possibile leggere, modificare, eliminare o elaborare tramite AI una nota inesistente
- ollama error checks
    - Ollama non sia raggiungibile;
    - il modello configurato non sia installato o disponibile;
    - la richiesta superi il tempo massimo previsto;
    - Ollama restituisca una risposta vuota o non valida

- 422 Unprocessable Entity per dati non validi;
- 503 Service Unavailable se Ollama non è disponibile.


---


Run with docker: 

- sudo docker compose up -d ollama
- sudo docker compose exec ollama ollama pull llama3.2:3b
- sudo docker compose up --build

Modello utilizzato: `llama3.2:3b` causa mancanza di GPU (CPU i5 12500T / RAM 32GB @3000Mhz) è un buon compromesso tra capacità e prestazioni.
