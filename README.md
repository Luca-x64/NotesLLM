# NotesLLM


### TODO
- search api validation date consistency
- pydantic validation
- ollama

Run with docker: 

sudo docker compose up -d ollama
sudo docker compose exec ollama ollama pull llama3.2:3b
sudo docker compose up --build

Modello utilizzato: `llama3.2:3b` causa mancanza di GPU (CPU i5 12500T / RAM 32GB @3000Mhz) è un buon compromesso tra capacità e prestazioni.
