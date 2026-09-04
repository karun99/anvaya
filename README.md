# Anvaya AI OS

> Anvaya remembers the researcher, not just the research.

A researcher-controlled AI memory that uses the researcher's context, history, and preferences to improve research discovery and AI-assisted workflows.

## Features

- **Research Memory** - Persistent, researcher-controlled research context
- **Personalized Retrieval** - Context-aware search and ranking
- **Evidence-Backed RAG** - Cited responses with source attribution
- **Document Ingestion** - PDF, DOCX, Markdown, and URL support
- **LLM Gateway** - Multi-provider AI model support
- **MCP Integration** - Tool and resource interoperability
- **Skills System** - Reusable research workflows
- **Energy Modes** - Configurable compute optimization
- **Local-First** - Optional local AI inference

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Vite |
| Backend | FastAPI + Python |
| Database | PostgreSQL + pgvector |
| Authentication | JWT |
| AI | Provider abstraction layer |
| Deployment | Docker |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Docker (optional)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd anvaya
```

2. Set up environment:
```bash
cp apps/api/.env.example apps/api/.env
# Edit .env with your configuration
```

3. Start with Docker:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r ../../requirements.txt
uvicorn apps.api.main:app --reload --port 8000
```

#### Frontend

```bash
cd apps/web
npm install
npm run dev
```

## Project Structure

```
anvaya/
├── apps/
│   ├── web/          # React frontend
│   └── api/          # FastAPI backend
├── core/
│   ├── memory/       # Research memory
│   ├── retrieval/    # Semantic retrieval
│   ├── ranking/      # Personalized ranking
│   ├── policies/     # AI governance
│   └── events/       # Event system
├── ai/
│   ├── gateway/      # LLM abstraction
│   ├── embeddings/   # Embedding providers
│   └── prompts/      # Prompt templates
├── integrations/
│   ├── mcp/          # MCP client
│   ├── agent_reach/  # Web research
│   └── unlimited_ocr/# OCR adapter
├── skills/
│   └── builtin/      # Built-in skills
└── tests/            # Test suite
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/token` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Researcher
- `GET /api/v1/researcher/profile` - Get profile
- `PUT /api/v1/researcher/profile` - Update profile
- `GET /api/v1/researcher/twin` - Get researcher twin

### Memory
- `GET /api/v1/memory/` - List memories
- `POST /api/v1/memory/` - Create memory
- `GET /api/v1/memory/{id}` - Get memory
- `PUT /api/v1/memory/{id}` - Update memory
- `DELETE /api/v1/memory/{id}` - Delete memory
- `POST /api/v1/memory/search` - Search memories

### Sources
- `GET /api/v1/sources/` - List sources
- `POST /api/v1/sources/` - Create source
- `GET /api/v1/sources/{id}` - Get source
- `PUT /api/v1/sources/{id}` - Update source
- `DELETE /api/v1/sources/{id}` - Delete source

### Documents
- `GET /api/v1/documents/` - List documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/{id}` - Get document
- `DELETE /api/v1/documents/{id}` - Delete document

### Search
- `POST /api/v1/search/` - Search sources

### Research
- `POST /api/v1/research/` - Conduct research

### Skills
- `GET /api/v1/skills/` - List skills
- `POST /api/v1/skills/` - Create skill
- `POST /api/v1/skills/run` - Run skill

### Energy
- `GET /api/v1/energy/status` - Get energy status
- `PUT /api/v1/energy/mode` - Update energy mode

## Configuration

Environment variables (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT secret key |
| `LLM_PROVIDER` | AI provider (openai, anthropic, etc.) |
| `LLM_API_KEY` | API key for LLM provider |
| `EMBEDDING_MODEL` | Embedding model name |
| `ENERGY_MODE` | Energy optimization mode |

## Energy Modes

- **PERFORMANCE** - Maximum speed and quality
- **BALANCED** - Good balance of speed and quality
- **ENERGY_SAVER** - Reduced compute, cache reuse
- **LOCAL_FIRST** - Prefer local inference
- **OFFLINE** - No external network operations

## Development

### Running Tests

```bash
pytest tests/
```

### Linting

```bash
# Backend
ruff check apps/api/ core/ ai/

# Frontend
cd apps/web && npm run lint
```

## License

MIT

## Acknowledgments

Built with the principle: "Start with memory. Prove personalization. Add integrations only where they increase research capability."
