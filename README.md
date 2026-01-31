# Gemini RAG Application

A real-time RAG (Retrieval-Augmented Generation) application using [Pathway](https://pathway.com) that provides always up-to-date knowledge from your documents, powered by Google's Gemini API.

## Features

- **Real-time document indexing** - Documents are automatically re-indexed when they change
- **Gemini 2.5 Flash** - Fast, cost-effective LLM for question answering
- **Gemini Embeddings** - Native Google embeddings (text-embedding-004)
- **Docling PDF Parser** - Advanced document parsing with table and image extraction
- **Google Drive integration** - Sync documents from Google Drive (optional)
- **Streamlit UI** - Simple web interface for asking questions

## Quick Start

### 1. Clone and Setup

```bash
# Copy environment template
cp .env.example .env

# Add your Gemini API key to .env
# Get one from: https://aistudio.google.com/app/apikey
```

### 2. Add Documents

Place your documents (PDF, DOCX, TXT, MD) in the `data/` folder.

### 3. Run with Docker

```bash
# Build and start
docker compose up --build

# Access:
# - Backend API: http://localhost:8000
# - Streamlit UI: http://localhost:8501
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/retrieve` | POST | Search documents without LLM |
| `/v1/statistics` | POST | Index health stats |
| `/v2/list_documents` | POST | List all indexed files |
| `/v2/answer` | POST | Ask questions (RAG) |
| `/v2/summarize` | POST | Summarize texts |

### Example: Ask a Question

```bash
curl -X POST http://localhost:8000/v2/answer \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the vacation policy?"}'
```

### Example: Filter by Document

```bash
curl -X POST http://localhost:8000/v2/answer \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the requirements?",
    "filters": "contains(path, `policy`)"
  }'
```

## Configuration

Edit `app.yaml` to customize:

- **LLM model** - Change Gemini version
- **Embedder** - Switch embedding models
- **Data sources** - Add Google Drive, SharePoint, etc.
- **Chunking** - Adjust token limits

### Enable Google Drive

1. Create a Google Cloud Project and enable Drive API
2. Create a Service Account and download credentials
3. Save credentials to `credentials/gdrive-service-account.json`
4. Share your Drive folder with the service account email
5. Uncomment the Google Drive source in `app.yaml`

## Project Structure

```
├── app.py              # Main Pathway application
├── app.yaml            # Configuration
├── requirements.txt    # Python dependencies
├── Dockerfile          # Backend container
├── docker-compose.yml  # Container orchestration
├── .env.example        # Environment template
├── data/               # Local documents
├── credentials/        # Google credentials
└── ui/
    ├── app.py          # Streamlit interface
    ├── Dockerfile      # UI container
    └── requirements.txt
```

## Deploy on Dokploy

### 1. Push to Git Repository

```bash
git add .
git commit -m "Add Dokploy deployment configuration"
git push origin main
```

### 2. Create Application in Dokploy

1. Go to your Dokploy dashboard
2. Create new **Application**
3. Select **Git** as source
4. Connect your repository

### 3. Configure Build Settings

- **Dockerfile Path**: `Dockerfile.dokploy`
- **Build Context**: `.` (root)

### 4. Set Environment Variables

Add these in Dokploy's environment variables:

```
GEMINI_API_KEY=your-gemini-api-key-here
PATHWAY_LICENSE_KEY=demo-license-key-with-telemetry
```

### 5. Configure Ports

Expose these ports:
- **8000** - Backend API
- **8501** - Streamlit UI (set as primary for web access)

### 6. Deploy

Click **Deploy** and wait for the build to complete. The application includes a health check that waits for the RAG index to be ready.

---

## Development

### Run Locally (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run backend
python app.py

# In another terminal, run UI
cd ui
pip install -r requirements.txt
streamlit run app.py
```

## Tech Stack

- **[Pathway](https://pathway.com)** - Real-time data processing framework
- **[Gemini](https://ai.google.dev)** - LLM and embeddings
- **[Docling](https://docling.ai)** - Document parsing
- **[Streamlit](https://streamlit.io)** - Web UI
- **[Docker](https://docker.com)** - Containerization

## License

MIT
