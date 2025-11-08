import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN environment variable not set.\n"
        "Please create a .env file with: HF_TOKEN=your_token"
    )

SMALL_EMBED_MODEL = "BAAI/bge-small-en-v1.5"
LARGE_EMBED_MODEL = "BAAI/bge-large-en-v1.5"
LLM_MODEL = "meta-llama/Llama-4-Scout-17B-16E-Instruct:groq"

SMALL_MODEL_CHUNK_THRESHOLD = 50

SMALL_MODEL_DIM = 384
LARGE_MODEL_DIM = 1024

QDRANT_URL = "http://localhost:6333"


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
CHUNK_SEPARATORS = ["\n\n", "\n", ".", " ", ""]

MAX_TOKENS = 512
DEFAULT_TOP_K = 5
BATCH_SIZE = 100

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

CORS_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]