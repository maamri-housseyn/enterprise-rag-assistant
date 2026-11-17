
# Enterprise RAG Assistant

An intelligent assistant for enterprise documents powered by Retrieval-Augmented Generation (RAG).

## Project Objective

The goal of this project is to build an AI-powered assistant capable of answering questions based on enterprise documents.

Instead of generating answers only from its internal knowledge, the assistant will retrieve relevant information from provided documents and use this context to generate more reliable, source-grounded answers.

## Technologies

- Python
- FastAPI
- PostgreSQL
- pgvector
- Hugging Face
- Large Language Models (LLMs)
- Docker

## Architecture

The application follows a modular architecture:

- `app/api`: API endpoints
- `app/core`: application configuration
- `app/database`: database connection and models
- `app/ingestion`: document processing and chunking
- `app/retrieval`: semantic search and retrieval
- `app/generation`: answer generation

## Current Progress

- [x] Initial project structure
- [x] FastAPI application
- [x] Health check endpoints
- [x] Git and GitHub setup
- [ ] PostgreSQL integration
- [ ] PDF document ingestion
- [ ] Vector embeddings
- [ ] Semantic search
- [ ] RAG answer generation
- [ ] Testing and evaluation

## Installation

Clone the repository:

```bash
git clone https://github.com/maamri-housseyn/enterprise-rag-assistant.git
cd enterprise-rag-assistant
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the API:

```powershell
uvicorn main:app --reload
```

Open the API documentation:

http://127.0.0.1:8000/docs

## Project Status

Currently under development.
