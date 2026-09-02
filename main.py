import os

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "") # TODO
DBPATH = os.environ.get("DBPATH", "") # TODO
TIMEOUT_REQUEST = int(os.environ.get("TIMEOUT_REQUEST", 2)) 

