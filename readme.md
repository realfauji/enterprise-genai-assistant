# Enterprise GenAI Assistant
A production-ready, multi-user Retrieval-Augmented Generation (RAG) based AI assistant built with:
- FastAPI (Async Backend)
- PostgreSQL
- LangChain
- FAISS Vector Store
- Streamlit Frontend
- JWT Authentication
- Usage & Cost Tracking

### Project Overview
Enterprise GenAI Assistant is a scalable, multi-user conversational AI platform that supports:
- Secure user authentication
- Session-based chat system
- Manual RAG implementation
- Conversational memory
- Document upload & indexing
- Token usage tracking
- Smart auto-title generation
- Hybrid LLM fallback (RAG + General Knowledge)
The system is designed using clean backend architecture principles and production-ready patterns.

### Architecture
User → Streamlit UI → FastAPI Backend → 
PostgreSQL (App DB)
FAISS (Vector Store)
LLM Provider (OpenAI / Groq)
Response

Core Layers:
- Authentication Layer (JWT)
- Session Management Layer
- Manual RAG Engine
- Token Usage Logging
- Cost Estimation Module
- Smart Title Generation

### Features
#### Authentication & Security
- JWT-based login & registration
- Protected API routes
- Multi-user isolation
#### Session-Based Chat
- Auto-create session on login
- Rename & delete sessions
- Sidebar chat history
- Persistent message history (DB-backend)
#### Document Upload & RAG
- PDF / TXT / CSV upload
- Recursive chunking with overlap
- FAISS vector store per user
- Hybrid retrieval + general knowledge fallback
- Context-aware prompt injection
#### Conversational Memory
- Stores conversation in DB
- Injects last 5 turns into LLM prompt
- Supports follow-up queries
#### Smart Auto Title Generation
- LLM-based dynamic title generation
- 5–6 word clean summary
- Automatically updates sidebar
#### Usage & Cost Tracking
- Token estimation
- Cost estimation per request
- Usage log stored in PostgreSQL

### Tech Stack
| Layer            | Technology         |
| ---------------- | ------------------ |
| Backend          | FastAPI (Async)    |
| Database         | PostgreSQL         |
| ORM              | SQLAlchemy (Async) |
| Vector DB        | FAISS              |
| LLM Integration  | LangChain          |
| Frontend         | Streamlit          |
| Auth             | JWT                |

### Running Locally
#### Clone Repository
git clone <your_repo_url>
cd enterprise-genai
#### Create Virtual Environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
#### Install Dependencies
pip install -r requirements.txt
#### Set Environment Variables
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
DATABASE_URL=postgresql+asyncpg://user:password@host/db
#### Run Backend
uvicorn app.main:app --reload
#### Run Frontend
streamlit run frontend/app.py

### Future Improvements
- Streaming responses
- Hybrid retrieval scoring
- Redis caching
- Admin dashboard (RBAC)
- Dockerized deployment

### Author
Raj Bhardwaj
Gen AI and FastAPI Python Developer
