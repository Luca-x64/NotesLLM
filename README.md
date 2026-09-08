# NotesLLM

NotesLLM is a small Python Backend application for managing notes through REST API.

The application supports creating, reading, updating, deleting and searching notes. <br>
It also integrates a local language model through Ollama to generate short summaries and suggest alternative titles.

The API provides endpoints for note CRUD operations, search/filtering, summarization, and title suggestions.

**Technologies**: Python $\cdot$ FastAPI $\cdot$ Pydantic $\cdot$ SQLite $\cdot$ Ollama $\cdot$ Docker

### Data persistance
Data persistence is handled using an SQLite database, chosen to simplify CRUD operations, especially filtering.
<br>The database is stored in a persistent Docker volume so that notes are not lost when containers are recreated.


### Ollama model

The model I used is: `llama3.2:3b` due to lack of a dedicated GPU.
<br>On an Intel Core i5-12500T with 32GB or RAM it provides a good balance between inference performance and response quality. 

The model can be set using the `OLLAMA_MODEL` environment variable.

### Running the project
1. Start ollama service: `sudo docker compose up -d ollama`
2. Download desired model: `sudo docker compose exec ollama ollama pull [model]` <br>for example: `sudo docker compose exec ollama ollama pull llama3.2:3b`
3. Start the app: `sudo docker compose up --build`

The FastAPI documentation is available at: `http://127.0.0.1:8000/docs`

### Configuration
Application settings can be changed through environment variables.
<br>An `.env` can be used, see an example in `.env.example`.

- OLLAMA_MODEL: ollama model used, for example `llama3.2:3b`
- OLLAMA_BASE_URL: base URL of the Ollama API service.
- DB_PATH: path to the SQLite database file, for example `/data/notes.db`
- TIMEOUT_REQUEST: timeout, in seconds, for requests sent to Ollama
- OLLAMA_API_RELATIVE_URL: relative Ollama API endpoint used by the application, for example `/api/chat`