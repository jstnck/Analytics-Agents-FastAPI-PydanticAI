# NBA Analytics Agent

A production-grade AI analytics platform demonstrating multi-agent orchestration for natural language data queries. This system enables business users to interact with complex NBA datasets using conversational English, automatically translating questions into optimized SQL queries with transparent execution paths.

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
- **Type-safe architecture** using Pydantic models throughout the stack
- **Conversation context** maintained across multi-turn interactions
- **Query transparency** showing generated SQL and execution metadata
- **Containerized** with async I/O, dependency injection, with docker compose

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
- **[Axios](https://axios-http.com/)** - HTTP client for API communication

### Infrastructure
- **Docker & Docker Compose** - Container orchestration
- **pytest** - Testing framework
- **Ruff** - Fast Python linter and formatter


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
   docker-compose up --build
   ```

4. **Access**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

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
└── docker-compose.yml      # Container orchestration
```

## Architecture

Hierarchical multi-agent system with specialized components:

```mermaid
graph TD
    A[User Query] --> B[Orchestrator Agent]
    B --> C[SQL Agent]
    C --> D[DuckDB Database]
    D --> E[Query Results]
    E --> C
    C --> B
    B --> F[Structured Response]
    F --> A
    
    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#f0f0f0
```

**Orchestrator Agent**: Routes requests based on intent and maintains conversation context  
**SQL Agent**: Generates and validates SQL queries with self-correction capabilities  
**DuckDB**: Analytics database with NBA team statistics, schedules, and ML predictions

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

## Testing

```bash
# Run backend tests
cd backend
pytest

# Run with coverage
pytest --cov=app tests/
```
