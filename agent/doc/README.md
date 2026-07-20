# Autonomous Engineering Council (Doc Agent)

The Doc Agent is an AI-powered architectural review tool that acts as an autonomous engineering council. It analyzes the git history and line-by-line diffs over a specified timeframe to generate a comprehensive, persona-driven weekly report.

## Core Features

- **Dynamic Personas:** Automatically assigns expert roles (e.g., Zero-Trust Security Architect, Senior Cloud/DevOps Engineer, Lead Data Scientist) based on the specific file paths modified in the commit history.
- **State Management:** Reads the most recent weekly report before generating a new one to track technical debt, ensuring continuity and follow-up on unresolved architectural issues.
- **Hallucination Prevention:** Enforces strict Large Language Model constraints (low temperature) and automatically aborts execution if the git diff lacks significant architectural changes.
- **Fail-Fast Architecture:** Validates the presence of required environment variables (such as GEMINI_API_KEY) prior to execution, providing actionable Developer Experience (DevEx) feedback if missing.

## Execution

The agent is seamlessly integrated into the project's native task runner and automatically loads local `.env` configurations.

To trigger the weekly review, execute:

```bash
task agent:doc
```

## Output & Artifacts

The agent generates a timestamped markdown report in the format `weekly_report_YYYY-MM-DD.md` within this directory.

To maintain repository hygiene and prevent bloat, these generated operational reports are explicitly ignored by version control (`.gitignore`) and remain strictly local to the execution environment.
