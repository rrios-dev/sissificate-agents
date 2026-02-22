# Sissificate Development Crew

Autonomous development agents for implementing DEV-TASKs from GitHub Projects using CrewAI.

## Prerequisites

- Python 3.10+ (3.13 recommended)
- OpenAI API key (or Anthropic/Gemini)
- GitHub Personal Access Token with `repo` and `project` scopes

## Installation

```bash
# Navigate to crew directory
cd /Users/roberto/Documents/projects/sissificate-agents/sissificate_dev

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```bash
# Required: OpenAI API key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# Required: GitHub token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Optional: Change model (default: gpt-4o)
OPENAI_MODEL_NAME=gpt-4o
```

## Usage

### Single Agent

```bash
# Auto-select next available task
python src/sissificate_dev/main.py

# Work on specific task
python src/sissificate_dev/main.py --task DEV-0101

# Work on specific epic
python src/sissificate_dev/main.py --epic PEPIC-002

# Dry run (no changes)
python src/sissificate_dev/main.py --dry-run
```

### Multiple Agents (Parallel)

Open multiple terminals and run:

```bash
# Terminal 1 - Agent 1
python src/sissificate_dev/main.py --agent-id 1 --epic PEPIC-002

# Terminal 2 - Agent 2  
python src/sissificate_dev/main.py --agent-id 2 --epic PEPIC-003

# Terminal 3 - Agent 3
python src/sissificate_dev/main.py --agent-id 3 --epic PEPIC-004
```

### Test Mode

```bash
python src/sissificate_dev/main.py --test
```

## Agent Types

| Agent | Role | Responsibilities |
|-------|------|------------------|
| `devops_coordinator` | DevOps Coordinator | Fetch tasks, lock issues, coordinate agents |
| `senior_frontend_engineer` | Senior Frontend Engineer | UI components, pages, styling |
| `senior_backend_engineer` | Senior Backend Engineer | API routes, database, validation |
| `qa_engineer` | QA Engineer | Tests, validation, quality checks |

## Workflow

1. **Fetch Task**: Coordinator queries GitHub for available DEV-TASKs
2. **Lock Task**: Issue status → "In Progress", lock file created
3. **Read Spec**: Parse DEV-TASK.md for requirements
4. **Implement Frontend**: Create/modify UI components
5. **Implement Backend**: Create/modify API routes
6. **Write Tests**: Create Playwright E2E tests
7. **Validate**: Run lint, build, tests
8. **Commit & Push**: Create feature branch, PR
9. **Update Issue**: Status → "In QA", add evidence

## Conflict Prevention

- **Lock Files**: `.lock.DEV-XXXX` prevents concurrent work
- **GitHub Status**: Only first agent to set "In Progress" wins
- **Epic Segregation**: Different agents work on different epics
- **Temporal Spacing**: Agents pick sequential DEV numbers

## Directory Structure

```
sissificate_dev/
├── .env                    # API keys and configuration
├── .env.example            # Template for .env
├── pyproject.toml          # Python dependencies
├── README.md               # This file
└── src/
    └── sissificate_dev/
        ├── __init__.py
        ├── main.py         # Entry point
        ├── crew.py         # Agent and task definitions
        ├── config/
        │   ├── agents.yaml # Agent configurations
        │   └── tasks.yaml  # Task definitions
        └── tools/
            └── __init__.py # Custom tools
```

## Troubleshooting

### "OPENAI_API_KEY not set"
Add your OpenAI API key to `.env`:
```bash
OPENAI_API_KEY=sk-xxxxxxxx
```

### "GITHUB_TOKEN not set"
Create a token at https://github.com/settings/tokens with scopes:
- `repo`
- `project`

### "Task already locked"
Another agent is working on this task. Either:
1. Wait for the lock to be released
2. Remove the lock file manually: `rm .lock.DEV-XXXX`
3. Work on a different task

### "Module not found"
Activate virtual environment and reinstall:
```bash
source .venv/bin/activate
pip install -e .
```

## Supported LLM Providers

CrewAI supports multiple LLM providers. To switch:

### OpenAI (default)
```bash
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL_NAME=gpt-4o
```

### Anthropic
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
# In crew.py, change llm parameter to: llm="claude-3-opus-20240229"
```

### Google Gemini
```bash
GEMINI_API_KEY=xxx
# In crew.py, change llm parameter to: llm="gemini/gemini-pro"
```

### Ollama (local)
```bash
# Install Ollama: https://ollama.ai
ollama pull llama3
# In crew.py, change llm parameter to: llm="ollama/llama3"
```

## Resources

- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI GitHub](https://github.com/crewAIInc/crewAI)
- [Sissificate Project](/Users/roberto/Documents/projects/sissificate)
- [GitHub Project Board](https://github.com/users/rrios-dev/projects/6)