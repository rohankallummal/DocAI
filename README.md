# DocAI

A full-stack RAG (Retrieval-Augmented Generation) application that allows users to upload PDF documents and ask questions about their content.


## Features

- **PDF Upload & Processing** - Upload PDFs and automatically chunk them for processing
- **Interactive Chat Interface** - Ask questions about your documents in natural language
- **Smart Retrieval** - Uses semantic search with vector embeddings (BGE models)
- **Dynamic Model Selection** - Automatically chooses between small/large embedding models based on document size
- **Configurable Retrieval** - Adjust the number of context chunks (top_k) for better answers
- **Session Management** - Reset and upload new documents anytime
- **Efficient Caching** - Caches embeddings to reduce API calls
- **Dockerized Vector DB** - Persistent Qdrant storage with Docker

## Tech Stack

### Backend
- **Framework:** FastAPI
- **Vector Database:** Qdrant
- **Embeddings:** HuggingFace (BAAI/bge-small-en-v1.5, BAAI/bge-large-en-v1.5)
- **LLM:** Meta Llama 4 Scout (via Groq)
- **PDF Processing:** PyPDF
- **Text Splitting:** LangChain

### Frontend
- **Framework:** React 18+
- **HTTP Client:** Axios
- **Icons:** Ionicons
- **Styling:** Custom CSS

### Infrastructure
- **Vector Storage:** Qdrant (Docker)
- **Language:** Python, JavaScript

---

**Flow:**
1. User uploads PDF → Backend chunks document → Generates embeddings → Stores in Qdrant
2. User asks question → Backend embeds question → Searches Qdrant → Retrieves relevant chunks → Sends to LLM → Returns answer

---

## Prerequisites

- **Python** 
- **Node.js** 
- **Docker** 
- **HuggingFace Account** 


## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rohankallummal/DocAI.git
cd DocAI
```

### 2. Backend Setup

```bash
cd rag-backend

# Create anaconda environment

conda create --name myenv python=3.10

# Activate virtual environment

conda activate myenv

```

### 3. Frontend Setup

```bash
cd DocAI

# Install dependencies
npm install
```

### 4. Docker Setup (Qdrant)

```bash

# Run Qdrant container

# Windows (CMD):
docker run -d --name qdrant -p 6333:6333 -v "%cd%/qdrant_storage:/qdrant/storage" qdrant/qdrant

```


## Configuration

### Backend Configuration

Create a `.env` file in `rag-backend/`:

```env
# HuggingFace API Token (Required)
HF_TOKEN= Your Access Token
```

---

## Running the Application

### Step 1: Start Qdrant

```bash
# Check if Qdrant is running
docker ps

# If not running, start it
docker start qdrant
```

### Step 2: Start Backend

```bash
cd rag-backend

conda activate myenv

# Run FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000
```


### Step 3: Start Frontend

```bash
cd DocAI

# Run development server
npm run dev

```

## Maintenance

### Clearing Cache & Storage

**Windows (PowerShell/CMD):**
```cmd
# Stop Qdrant container
docker stop qdrant

# Delete Qdrant storage
rmdir /s /q "D:\DocAI\rag-backend\qdrant_storage"

# Delete embedding cache
rmdir /s /q "D:\DocAI\rag-backend\cache"

# Restart Qdrant
docker start qdrant
```

