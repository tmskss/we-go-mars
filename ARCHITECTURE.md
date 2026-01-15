# We Go Mars - AI Science Research Planner (Hackathon PoC)

A multi-agent system that transforms a research hypothesis into a detailed, actionable research plan using parallel judge voting and tree-of-thoughts reasoning.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ |
| Agent Framework | Microsoft AutoGen |
| LLM | Configurable (GPT-4o, GPT-5, etc.) |
| Vector Database | Qdrant |
| Deployment | Docker Compose |

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESEARCH PLAN GENERATOR                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. USER HYPOTHESIS                                                          │
│         │                                                                    │
│         v                                                                    │
│  2. DEEP RESEARCH AGENT ──> Clarifying Questions ──> User Answers           │
│         │                                                                    │
│         v                                                                    │
│  3. HIGH-LEVEL REQUIREMENTS                                                  │
│         │                                                                    │
│         v                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  4. REQUIREMENT TREE BREAKDOWN (Parallel)                           │    │
│  │     ┌─────────────────────────────────────────────────────────┐     │    │
│  │     │  JUDGES (Majority Vote)                                 │     │    │
│  │     │  ├── Atomicness Judge x3                                │     │    │
│  │     │  └── Feasibility Judge x3                               │     │    │
│  │     └─────────────────────────────────────────────────────────┘     │    │
│  │              │                                                       │    │
│  │              v                                                       │    │
│  │     Both Pass? ──No──> SUGGESTORS x3 (Majority Vote) ──> Retry      │    │
│  │              │                                                       │    │
│  │             Yes                                                      │    │
│  │              │                                                       │    │
│  │              v                                                       │    │
│  │     FEASIBLE ATOMIC REQUIREMENTS                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│         │                                                                    │
│         v                                                                    │
│  5. CONTEXT SEARCH ──> Split: Has Solution? / Needs Solution                │
│         │                                                                    │
│         v                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  6. THE SOLVER (Parallel)                                           │    │
│  │     ┌─────────────────────────────────────────────────────────┐     │    │
│  │     │  PROPOSERS x3 (Each uses N-Tree of Thoughts)            │     │    │
│  │     │  └── Generate candidate solutions                       │     │    │
│  │     └─────────────────────────────────────────────────────────┘     │    │
│  │              │                                                       │    │
│  │              v                                                       │    │
│  │     ┌─────────────────────────────────────────────────────────┐     │    │
│  │     │  SOLUTION JUDGES x3 (Majority Vote)                     │     │    │
│  │     │  └── Evaluate quality                                   │     │    │
│  │     └─────────────────────────────────────────────────────────┘     │    │
│  │              │                                                       │    │
│  │              v                                                       │    │
│  │     Quality OK? ──No──> Retry with feedback                         │    │
│  │              │                                                       │    │
│  │             Yes                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│         │                                                                    │
│         v                                                                    │
│  7. SOLUTION AGGREGATOR                                                      │
│         │                                                                    │
│         v                                                                    │
│  8. RESEARCH PLAN SYNTHESIZER                                                │
│         │                                                                    │
│         v                                                                    │
│  OUTPUT: RESEARCH PLAN WITH CLEAR GOALS                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
we-go-mars/
├── pyproject.toml
├── README.md
├── ARCHITECTURE.md
├── .env.example
├── docker-compose.yml
├── Dockerfile
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   ├── config.py                  # LLM & app configuration
│   │
│   ├── agents/                    # AutoGen agent definitions
│   │   ├── __init__.py
│   │   ├── deep_researcher.py     # Initial research & questions
│   │   ├── requirement_decomposer.py
│   │   ├── atomicness_judge.py    # Judge if requirement is atomic
│   │   ├── feasibility_judge.py   # Judge if requirement is feasible
│   │   ├── suggestor.py           # Suggests refinements
│   │   ├── proposer.py            # Tree-of-thoughts solution proposer
│   │   ├── solution_judge.py      # Evaluates solution quality
│   │   ├── aggregator.py          # Combines all solutions
│   │   └── plan_synthesizer.py    # Final plan generation
│   │
│   ├── orchestration/             # Workflow coordination
│   │   ├── __init__.py
│   │   ├── workflow.py            # Main workflow orchestrator
│   │   ├── voting.py              # Majority vote logic
│   │   └── tree_of_thoughts.py    # ToT implementation
│   │
│   ├── rag/                       # Knowledge base
│   │   ├── __init__.py
│   │   ├── literature_store.py    # Literature RAG
│   │   ├── embeddings.py          # Embedding generation
│   │   └── retrieval.py           # Context retrieval
│   │
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── hypothesis.py
│   │   ├── requirement.py
│   │   ├── solution.py
│   │   └── research_plan.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── logging.py
│
└── data/
    └── papers/                    # Sample papers for RAG
```

---

## Agent Definitions (AutoGen)

### 1. Deep Researcher
```python
# Researches the hypothesis and generates clarifying questions
class DeepResearcherAgent:
    - Input: User hypothesis
    - Actions: Search literature, identify gaps
    - Output: Initial context + clarifying questions for user
```

### 2. Requirement Decomposer
```python
# Breaks high-level requirements into tree structure
class RequirementDecomposerAgent:
    - Input: High-level requirements + context
    - Actions: Recursive decomposition
    - Output: Requirement tree (may not be atomic yet)
```

### 3. Atomicness Judges (x3)
```python
# Judges if a requirement is atomic (can't be broken down further)
class AtomicnessJudgeAgent:
    - Input: Single requirement
    - Output: {is_atomic: bool, reasoning: str}
    - Note: 3 instances, majority vote decides
```

### 4. Feasibility Judges (x3)
```python
# Judges if a requirement is feasible to solve
class FeasibilityJudgeAgent:
    - Input: Single requirement + context
    - Output: {is_feasible: bool, reasoning: str}
    - Note: 3 instances, majority vote decides
```

### 5. Suggestors (x3)
```python
# Suggests how to refine non-atomic/non-feasible requirements
class SuggestorAgent:
    - Input: Requirement + judge feedback
    - Output: Suggested refinement approach
    - Note: 3 instances, majority vote on best suggestion
```

### 6. Proposers (x3)
```python
# Generates solution candidates using Tree of Thoughts
class ProposerAgent:
    - Input: Atomic requirement + context
    - Actions: N-Tree of Thoughts exploration
    - Output: Candidate solutions with reasoning chains
```

### 7. Solution Judges (x3)
```python
# Evaluates solution quality
class SolutionJudgeAgent:
    - Input: Candidate solution + requirement
    - Output: {quality_score: float, is_acceptable: bool, feedback: str}
    - Note: 3 instances, majority vote decides
```

### 8. Aggregator
```python
# Combines all solutions
class AggregatorAgent:
    - Input: All approved solutions (existing + novel)
    - Output: Unified solution set with relationships
```

### 9. Plan Synthesizer
```python
# Generates final research plan
class PlanSynthesizerAgent:
    - Input: Aggregated solutions + original hypothesis
    - Output: Structured research plan with clear goals
```

---

## Data Models

### Requirement
```python
class Requirement:
    id: str
    parent_id: str | None
    content: str
    level: int                    # Depth in tree
    is_atomic: bool | None        # Set by judges
    is_feasible: bool | None      # Set by judges
    children: list[Requirement]
    solution: Solution | None
```

### Solution
```python
class Solution:
    requirement_id: str
    content: str
    reasoning_chain: list[str]    # Tree of Thoughts path
    source: str                   # "existing" | "novel"
    confidence: float
```

### ResearchPlan
```python
class ResearchPlan:
    hypothesis: str
    goals: list[str]
    methodology: list[Step]
    expected_outcomes: list[str]
    requirements_tree: Requirement
    solutions: list[Solution]
```

---

## Implementation Phases

### Phase 1: Project Setup (Day 1 Morning)
- [ ] Initialize `pyproject.toml` with dependencies
- [ ] Create `config.py` with LLM configuration
- [ ] Set up `docker-compose.yml` (app + Qdrant)
- [ ] Create `.env.example`

### Phase 2: Core Models (Day 1 Morning)
- [ ] Implement `models/requirement.py`
- [ ] Implement `models/solution.py`
- [ ] Implement `models/research_plan.py`

### Phase 3: RAG Setup (Day 1 Afternoon)
- [ ] Implement `rag/embeddings.py`
- [ ] Implement `rag/literature_store.py`
- [ ] Implement `rag/retrieval.py`

### Phase 4: Agents (Day 1 Afternoon - Day 2 Morning)
- [ ] Implement `agents/deep_researcher.py`
- [ ] Implement `agents/requirement_decomposer.py`
- [ ] Implement `agents/atomicness_judge.py`
- [ ] Implement `agents/feasibility_judge.py`
- [ ] Implement `agents/suggestor.py`
- [ ] Implement `agents/proposer.py` (with ToT)
- [ ] Implement `agents/solution_judge.py`
- [ ] Implement `agents/aggregator.py`
- [ ] Implement `agents/plan_synthesizer.py`

### Phase 5: Orchestration (Day 2 Afternoon)
- [ ] Implement `orchestration/voting.py`
- [ ] Implement `orchestration/tree_of_thoughts.py`
- [ ] Implement `orchestration/workflow.py`

### Phase 6: CLI & Integration (Day 2 Evening)
- [ ] Implement `main.py` CLI
- [ ] End-to-end testing with sample hypothesis

---

## Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM Configuration (GPT-5 family)
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"  # or gpt-5, gpt-5-turbo, etc.
    llm_api_key: str
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Workflow
    max_refinement_iterations: int = 5
    judge_count: int = 3              # For majority voting
    proposer_count: int = 3
    tree_of_thoughts_branches: int = 3
    tree_of_thoughts_depth: int = 3

    class Config:
        env_file = ".env"
```

---

## Docker Services

```yaml
# docker-compose.yml
version: "3.9"

services:
  app:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LLM_MODEL=${LLM_MODEL:-gpt-4o}
      - QDRANT_HOST=qdrant
    depends_on:
      - qdrant
    volumes:
      - ./data:/app/data

  qdrant:
    image: qdrant/qdrant:v1.9.0
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

---

## Dependencies

```toml
[project]
name = "we-go-mars"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
    "openai>=1.12.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.2.0",
    "qdrant-client>=1.8.0",
    "tiktoken>=0.6.0",
    "rich>=13.7.0",               # Nice CLI output
    "typer>=0.9.0",               # CLI framework
]
```

---

## CLI Usage

```bash
# Run the research planner
python -m src.main "Your research hypothesis here"

# With custom model
python -m src.main "Your hypothesis" --model gpt-5

# With papers directory for RAG
python -m src.main "Your hypothesis" --papers ./data/papers/
```

---

## Output Format

The final output is a `ResearchPlan` rendered as:

```markdown
# Research Plan: [Hypothesis Summary]

## Goals
1. [Clear goal 1]
2. [Clear goal 2]
...

## Methodology
### Step 1: [Step name]
- Description: ...
- Expected output: ...

### Step 2: [Step name]
...

## Requirements Breakdown
[Tree visualization]

## Solutions
### For requirement X:
- Approach: ...
- Reasoning: ...

## Expected Outcomes
1. ...
2. ...

## Next Steps
1. ...
```

---

## Key Files to Implement First

1. `src/config.py` - LLM configuration
2. `src/models/requirement.py` - Core data structure
3. `src/orchestration/voting.py` - Majority vote logic
4. `src/orchestration/workflow.py` - Main orchestrator
5. `src/agents/proposer.py` - Tree of Thoughts solver
