# Gemini RAG Application Design

## Overview

A real-time RAG (Retrieval-Augmented Generation) application using Pathway that provides always up-to-date knowledge from Google Drive documents, powered by Google's Gemini API.

## Requirements

| Aspect | Choice |
|--------|--------|
| **Data Source** | Google Drive |
| **Use Case** | Internal knowledge base (team docs, policies, procedures) |
| **Deployment** | Docker container |
| **Interface** | Streamlit UI |
| **LLM** | Gemini 2.5 Flash |
| **Embeddings** | Gemini text-embedding-004 |
| **PDF Parser** | Docling |
| **Features** | Basic RAG |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Google Drive                            │
│                    (Team Documents)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │ polls every 30s
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Pathway Backend                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Docling   │→ │  Splitter   │→ │  Gemini Embedder    │  │
│  │   Parser    │  │ (400 tokens)│  │ (text-embedding-004)│  │
│  └─────────────┘  └─────────────┘  └──────────┬──────────┘  │
│                                                │             │
│                                    ┌───────────▼──────────┐ │
│                                    │   USearch Vector DB  │ │
│                                    └───────────┬──────────┘ │
│                                                │             │
│  ┌─────────────────────────────────────────────▼──────────┐ │
│  │              Gemini 2.5 Flash (RAG)                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│              REST API (port 8000)                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI                              │
│                     (port 8501)                              │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
konyankg-exam/
├── app.py                 # Main Pathway application
├── app.yaml               # Configuration (LLM, embedder, sources)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Container orchestration
├── .env                   # Gemini API key (not committed)
├── .env.example           # Template for env vars
├── credentials/           # Google service account credentials
│   └── gdrive-service-account.json
├── data/                  # Local test data (optional fallback)
└── ui/
    └── app.py             # Streamlit interface
```

## Configuration (app.yaml)

```yaml
# LLM - Gemini 2.5 Flash via LiteLLM
$llm: !pw.xpacks.llm.llms.LiteLLMChat
  model: "gemini/gemini-2.5-flash-preview-05-20"
  retry_strategy: !pw.udfs.ExponentialBackoffRetryStrategy
    max_retries: 6
  cache_strategy: !pw.udfs.DefaultCache {}
  temperature: 0
  capacity: 8

# Embeddings - Gemini native embedder
$embedder: !pw.xpacks.llm.embedders.GeminiEmbedder
  model: "models/text-embedding-004"

# Document parser - Docling with Gemini for images/tables
$parser: !pw.xpacks.llm.parsers.DoclingParser
  parse_images: true
  table_parsing_strategy: "llm"
  image_parsing_strategy: "llm"
  multimodal_llm: $llm
  pdf_pipeline_options:
    do_formula_enrichment: true
    image_scale: 1.5

# Text splitting - 400 tokens per chunk
$splitter: !pw.xpacks.llm.splitters.TokenCountSplitter
  max_tokens: 400

# Data source - Google Drive folder
$sources:
  - !pw.io.gdrive.read
    object_id: "YOUR_FOLDER_ID"
    service_user_credentials_file: "credentials/gdrive-service-account.json"
    with_metadata: true
    refresh_interval: 30
  - !pw.io.fs.read
    path: "data"
    format: binary
    with_metadata: true

# Vector index
$retriever_factory: !pw.stdlib.indexing.UsearchKnnFactory
  reserved_space: 1000
  embedder: $embedder
  metric: !pw.stdlib.indexing.USearchMetricKind.COS

# Document store
$document_store: !pw.xpacks.llm.document_store.DocumentStore
  docs: $sources
  parser: $parser
  splitter: $splitter
  retriever_factory: $retriever_factory

# Question answerer
question_answerer: !pw.xpacks.llm.question_answering.BaseRAGQuestionAnswerer
  llm: $llm
  indexer: $document_store
  search_topk: 6

# Server
host: "0.0.0.0"
port: 8000

# Cache
persistence_mode: !pw.PersistenceMode.UDF_CACHING
persistence_backend: !pw.persistence.Backend.filesystem
  path: ".cache"
```

## Docker Configuration

### docker-compose.yml

```yaml
version: "3.8"
services:
  rag-backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./credentials:/app/credentials
      - ./.cache:/app/.cache
    env_file:
      - .env
    restart: unless-stopped

  rag-ui:
    build: ./ui
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://rag-backend:8000
    depends_on:
      - rag-backend
    restart: unless-stopped
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### requirements.txt

```
pathway[all]>=0.14.0
docling>=2.0.0
google-generativeai>=0.5.0
litellm>=1.30.0
python-dotenv>=1.0.0
```

## Environment Variables

### .env

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/retrieve` | POST | Search documents without LLM |
| `/v1/statistics` | POST | Index health stats |
| `/v2/list_documents` | POST | List all indexed files |
| `/v2/answer` | POST | Ask questions (RAG) |

## Example Usage

```bash
# Ask a question
curl -X POST http://localhost:8000/v2/answer \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is our vacation policy?"}'

# Filter by file
curl -X POST http://localhost:8000/v2/answer \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the requirements?",
    "filters": "contains(path, `onboarding`)"
  }'

# Check index stats
curl -X POST http://localhost:8000/v1/statistics
```

## Google Drive Setup

1. Create a Google Cloud Project and enable the Google Drive API
2. Create a Service Account with Drive read access
3. Download credentials JSON → save as `credentials/gdrive-service-account.json`
4. Share your Drive folder with the service account email
5. Get folder ID from the Drive URL (last part of `https://drive.google.com/drive/folders/FOLDER_ID`)
6. Update `object_id` in `app.yaml`

## Running the Application

```bash
# Build containers
docker compose build

# Start services
docker compose up

# Access
# - Backend API: http://localhost:8000
# - Streamlit UI: http://localhost:8501
```
