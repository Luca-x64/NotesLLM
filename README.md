# NotesLLM


Data persistence is handled using an SQLite database, chosen to simplify CRUD operations, especially filtering.

- `sudo docker compose up -d ollama`
- `sudo docker compose exec ollama ollama pull [model]` 
- `sudo docker compose up --build`

for example : `sudo docker compose exec ollama ollama pull llama3.2:3b`

The model i used is: `llama3.2:3b` due to lack of a dedicated GPU.
On an Intel core i5-12500T with 32GB or RAM it provides a good balance between inference performance and response quality. 