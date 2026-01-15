# We Go Mars

AI-first science platform for hypothesis-driven research planning using multi-agent systems.

## Overview

This platform transforms a research hypothesis into a detailed, actionable research plan using:

- **Multi-agent orchestration** with Microsoft Agent Framework
- **Majority voting** for quality control (3 judges per decision)
- **Tree of Thoughts** reasoning for solution generation
- **RAG** for literature context retrieval

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- OpenAI API key

### Setup

```bash
# 1. Clone and enter the repo
cd we-go-mars

# 2. Copy environment file and add your API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Start Qdrant (vector database)
docker-compose up -d qdrant

# 4. Install dependencies
pip install -e .
# OR with uv:
uv pip install -e .

# 5. Run the app
python -m src.main "Your research hypothesis here"
```
## Setup deep research
```bash
git clone https://github.com/dzhng/deep-research
cd deep-research   
npm install
npm install -D dotenv dotenv-cli
create deep-research/.env.local (on discord)
```


### Using Docker

```bash
# Build and run everything
docker-compose up --build
```

## Project Structure

```
we-go-mars/
├── src/
│   ├── main.py              # CLI entry point
│   ├── config.py            # Configuration
│   ├── agents/              # All agent implementations
│   ├── orchestration/       # Workflow & voting logic
│   ├── rag/                 # RAG system
│   ├── models/              # Data models
│   └── utils/               # Utilities
├── data/                    # Papers for RAG ingestion
├── ARCHITECTURE.md          # Detailed architecture docs
└── docker-compose.yml       # Docker services
```

## Workflow

```
User Hypothesis
      │
      ▼
┌─────────────────┐
│ Deep Researcher │ ──► Clarifying Questions
└─────────────────┘
      │
      ▼
┌─────────────────────┐
│ Requirement         │
│ Decomposer          │ ──► Requirement Tree
└─────────────────────┘
      │
      ▼
┌─────────────────────┐     ┌───────────┐
│ Atomicness Judges   │ ◄──►│ Suggestors│
│ Feasibility Judges  │     └───────────┘
│ (Majority Vote x3)  │
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ Proposers x3        │
│ (Tree of Thoughts)  │
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ Solution Judges x3  │
│ (Majority Vote)     │
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ Aggregator          │
│ Plan Synthesizer    │
└─────────────────────┘
      │
      ▼
   Research Plan
```

---

## Team Assignment

Each module has an `Owner: [ASSIGN TEAMMATE]` marker. Assign teammates below:

### Core Components

| Component | File(s) | Owner | Priority |
|-----------|---------|-------|----------|
| **Config** | `src/config.py` | | P0 |
| **CLI/Main** | `src/main.py` | | P1 |
| **Workflow Orchestrator** | `src/orchestration/workflow.py` | | P0 |
| **Voting Logic** | `src/orchestration/voting.py` | | P0 |

### Agents

| Agent | File | Owner | Priority |
|-------|------|-------|----------|
| **Base Agent** | `src/agents/base.py` | | P0 |
| **Deep Researcher** | `src/agents/deep_researcher.py` | | P1 |
| **Requirement Decomposer** | `src/agents/requirement_decomposer.py` | | P1 |
| **Atomicness Judge** | `src/agents/atomicness_judge.py` | | P1 |
| **Feasibility Judge** | `src/agents/feasibility_judge.py` | | P1 |
| **Suggestor** | `src/agents/suggestor.py` | | P2 |
| **Proposer (ToT)** | `src/agents/proposer.py` | | P1 |
| **Solution Judge** | `src/agents/solution_judge.py` | | P1 |
| **Aggregator** | `src/agents/aggregator.py` | | P2 |
| **Plan Synthesizer** | `src/agents/plan_synthesizer.py` | | P2 |

### RAG System

| Component | File | Owner | Priority |
|-----------|------|-------|----------|
| **Embeddings** | `src/rag/embeddings.py` | | P1 |
| **Literature Store** | `src/rag/literature_store.py` | | P1 |
| **Retrieval Service** | `src/rag/retrieval.py` | | P1 |

### Models

| Model | File | Owner | Priority |
|-------|------|-------|----------|
| **Hypothesis** | `src/models/hypothesis.py` | | P0 |
| **Requirement** | `src/models/requirement.py` | | P0 |
| **Solution** | `src/models/solution.py` | | P0 |
| **Research Plan** | `src/models/research_plan.py` | | P1 |

### Special Tasks

| Task | File(s) | Owner | Priority |
|------|---------|-------|----------|
| **Tree of Thoughts** | `src/orchestration/tree_of_thoughts.py` | | P1 |

---

## Implementation Notes

### Priority Guide
- **P0**: Must have for demo - implement first
- **P1**: Core functionality - implement second
- **P2**: Nice to have - implement if time permits

### TODO Markers

Every file contains `TODO:` markers showing what needs to be implemented. Search for them:

```bash
grep -r "TODO:" src/
```

### Key Integration Points

1. **Workflow → Agents**: `workflow.py` calls all agents
2. **Agents → RAG**: Agents use `RetrievalService` for context
3. **Voting**: All judge results go through `voting.py`
4. **ToT**: Proposers use `TreeOfThoughts` class

### Testing Your Component

```python
# Example: Test your agent in isolation
import asyncio
from src.agents.your_agent import YourAgent

agent = YourAgent()
result = asyncio.run(agent.execute(your_input))
print(result)
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | (required) |
| `LLM_MODEL` | Model to use | `gpt-4o` |
| `LLM_TEMPERATURE` | Temperature | `0.7` |
| `QDRANT_HOST` | Qdrant host | `localhost` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `JUDGE_COUNT` | Number of judges | `3` |
| `PROPOSER_COUNT` | Number of proposers | `3` |

---

## Architecture Docs

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation including:
- Complete workflow diagram
- Agent specifications
- Data models
- Implementation phases
