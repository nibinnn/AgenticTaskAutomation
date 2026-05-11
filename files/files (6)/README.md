# Multi-Agent Task Automation System 🤖

AI-powered multi-agent pipeline engine. Describe what you want in plain English — Claude designs and executes the workflow.

---

## Quick Start

```bash
# 1. Clone / copy the project
cd agent-project

# 2. Set your API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# 3. Build the image
docker compose build

# 4. Run the AI-generated pipeline demo
docker compose run --rm auto
```

---

## Docker Commands

### Build
```bash
docker compose build
# or plain docker:
docker build -t agent-system:latest .
```

### Run modes

| Command | What it does |
|---|---|
| `docker compose run --rm auto` | AI generates & runs 4 demo pipelines |
| `docker compose run --rm demo` | Runs the manual-pipeline demo |
| `docker compose run --rm test` | Smoke tests (no API key needed) |
| `docker compose run --rm shell` | Interactive bash shell |

### One-shot solver — give it any requirement

```bash
# Simplest form
REQUIREMENT="Summarize the key insights from my sales data" \
ANTHROPIC_API_KEY=sk-ant-... \
docker compose run --rm solver

# With inline context data
REQUIREMENT="Filter products with revenue above 2000 and save as CSV" \
CONTEXT_JSON='[{"product":"A","revenue":1200},{"product":"B","revenue":3400}]' \
docker compose run --rm solver

# Using .env file
docker compose --env-file .env run --rm solver
```

### Plain Docker (no compose)

```bash
# Run auto demo
docker run --rm \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  agent-system:latest auto

# Solve a requirement
docker run --rm \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e REQUIREMENT="Generate a Python retry utility and critique it" \
  agent-system:latest solve

# Drop into shell
docker run --rm -it \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  agent-system:latest shell

# Run your own script
docker run --rm \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -v $(pwd)/my_script.py:/app/my_script.py \
  agent-system:latest python my_script.py
```

---

## Architecture

```
agent-project/
├── Dockerfile              # Multi-stage build (base → deps → final)
├── docker-compose.yml      # Service profiles: auto, demo, solver, test, dev
├── entrypoint.sh           # Smart entrypoint with mode switching
├── requirements.txt        # Python dependencies
├── .env.example            # Copy to .env and fill in API key
│
├── main.py                 # Manual pipeline demo
├── main_auto.py            # AI-generated pipeline demo
├── orchestrator.py         # Manual orchestrator
├── auto_orchestrator.py    # AI-driven orchestrator
│
└── agents/
    ├── base_agent.py       # Abstract BaseAgent + TaskResult
    ├── ai_agent.py         # Claude API agent (reason, summarize, extract, etc.)
    ├── planner_agent.py    # Converts requirements → pipeline JSON
    ├── specialized_agents.py  # DataAgent, FileAgent, TransformAgent, SchedulerAgent
    └── __init__.py
```

### Agent capabilities

| Agent | Operations |
|---|---|
| **AIAgent** | reason, summarize, extract, classify, code_gen, generate, plan, critique |
| **DataAgent** | analyze, filter, sort, aggregate, summarize, validate |
| **TransformAgent** | json_to_csv, csv_to_json, flatten, encode, template, extract |
| **FileAgent** | write, read, list, delete, checksum, search |
| **SchedulerAgent** | schedule, chain |
| **PlannerAgent** | Reads requirements → designs pipeline JSON |

---

## Using the SDK in your own code

```python
from auto_orchestrator import AutoOrchestrator

orc = AutoOrchestrator(api_key="sk-ant-...")

result = orc.solve(
    "Analyze this sales data, find top products, write AI insights, save as CSV",
    context={"data": [
        {"product": "A", "revenue": 1200},
        {"product": "B", "revenue": 3400},
    ]}
)

print(result["goal_summary"])
print(result["final_output"])
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | **Required** for AI features |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `RUN_MODE` | `auto` | Default run mode |
| `REQUIREMENT` | — | Used by the `solver` service |
| `CONTEXT_JSON` | — | JSON data passed to the solver |

---

## Development

```bash
# Mount source for live editing
docker compose --profile dev run --rm shell

# Run a specific script
docker run --rm -it \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -v $(pwd):/app \
  agent-system:latest python my_experiment.py
```
