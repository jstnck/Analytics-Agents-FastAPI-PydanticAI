# NBA Analytics Agent

A deployment-ready AI analytics platform demonstrating multi-agent orchestration for natural language data queries. This system enables business users to interact with complex NBA datasets using conversational English, automatically translating questions into optimized SQL queries with transparent execution paths.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/next.js-15.1-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)](https://www.typescriptlang.org/)

## Overview

This application showcases a modern approach to data analytics through a **hierarchical multi-agent architecture** built with PydanticAI. The system implements specialized AI agents that collaborate to transform natural language queries into actionable database insights.

### Key Features

- **Multi-agent orchestration** with specialized routing and intent classification
- **Natural language to SQL** with automatic query generation and error recovery
- **Chart visualizations** powered by Plotly for query results
- **Type-safe architecture** using Pydantic models throughout the stack
- **Conversation context** maintained across multi-turn interactions
- **Query transparency** showing generated SQL and execution metadata
- **Production-ready infrastructure** with nginx reverse proxy and containerized services

## Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern async web framework
- **[PydanticAI](https://ai.pydantic.dev/)** - Type-safe AI agent framework (by the Pydantic team)
- **[Claude Sonnet 4](https://www.anthropic.com/claude)** - Anthropic's latest LLM for agent intelligence
- **[DuckDB](https://duckdb.org/)** - High-performance analytical database
- **Python 3.11+** with async/await throughout

### Frontend
- **[Next.js 15](https://nextjs.org/)** - React framework with App Router
- **[TypeScript](https://www.typescriptlang.org/)** - Type safety in the frontend
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first styling
- **[Plotly.js](https://plotly.com/javascript/)** - Interactive data visualization
- **[Axios](https://axios-http.com/)** - HTTP client for API communication

### Infrastructure
- **nginx** - Reverse proxy for unified service routing
- **Docker & Docker Compose** - Container orchestration
- **pytest** - Testing framework
- **Ruff and Mypy** - Fast Python linter type checking


## Use Cases

**Data Exploration**
- Interactive schema discovery
- Rapid hypothesis testing
- Pattern recognition in game statistics

**Decision Support**
- ML prediction interpretation: LLMs are able to access results of machine learning models
- Scenario analysis with what-if queries
- Performance metric calculation
- "Compare the Raptors and Celtics offensive performance"
- "What are the ML predictions for upcoming games?"


## Getting Started

### Prerequisites

- Docker and Docker Compose
- Anthropic API key or OpenAI API key

### Running the Application

1. **Clone and navigate**
   ```bash
   git clone <your-repo-url>
   cd analysis-agent-mvp2
   ```

2. **Configure environment**
   
   Create `backend/.env`:
   ```bash
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **Launch**
   ```bash
   docker compose up --build
   ```

4. **Access**
   - Application: [http://localhost:8080](http://localhost:8080)
   - API Docs: [http://localhost:8080/api/v1/docs](http://localhost:8080/api/v1/docs)

   The application uses nginx as a reverse proxy that routes:
   - `/api/*` requests to the FastAPI backend
   - All other requests to the Next.js frontend

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # PydanticAI agent implementations
│   │   │   ├── orchestrator.py   # Main routing agent
│   │   │   ├── sql_agent.py      # SQL generation agent
│   │   │   └── tools.py          # Shared agent tools
│   │   ├── api/            # FastAPI routes
│   │   ├── database/       # DuckDB client
│   │   ├── schemas/        # Pydantic models
│   │   └── utils/          # Prompts and helpers
│   └── tests/              # Pytest test suite
├── frontend-nextjs/        # Next.js frontend
│   └── src/
│       ├── app/            # App router pages
│       ├── components/     # React components
│       └── lib/            # API client & types
├── data/                   # DuckDB database files
├── nginx.conf              # Reverse proxy configuration
└── docker-compose.yml      # Container orchestration
```

## Architecture

### Infrastructure Layer

```mermaid
graph LR
    A[Browser] -->|:8080| B[nginx]
    B -->|/api/*| C[FastAPI Backend :8000]
    B -->|/*| D[Next.js Frontend :3000]
    C --> E[DuckDB]

    style B fill:#90EE90
    style C fill:#87CEEB
    style D fill:#FFB6C1
    style E fill:#f0f0f0
```

### Agent System

Hierarchical multi-agent system: the orchestrator chats with the user, and coordinates data analysis and charts from the sub agents:

```mermaid
graph TD
    A[User Query] --> B[Orchestrator Agent]
    B <--> C[SQL Agent]
    B <--> D[Visualization Agent]
    C <--> E[DuckDB]
    B --> A

    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#ffe1f5
    style E fill:#f0f0f0
```

## Testing

The project includes comprehensive test coverage for core functionality:

```bash
# Execute full test suite
cd backend
pytest -v

# Generate coverage report
pytest --cov=app --cov-report=html tests/

# Run specific test categories
pytest tests/test_agents.py -v      # Agent functionality
pytest tests/test_api.py -v         # API endpoints
```

### Test Coverage

- Database query execution and validation
- SQL injection prevention mechanisms
- Agent tool integration
- Error handling and recovery paths
- API endpoint responses and status codes

## Contributing

Contributions are welcome. Please submit pull requests with:
- Clear description of changes
- Updated tests for new functionality
- Documentation updates as needed

For major changes, please open an issue first to discuss the proposed modifications.
