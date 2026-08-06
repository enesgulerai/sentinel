<div align="left">

# Sentinel: Enterprise Real-Time Fraud & Anomaly Ingestion Engine
### Module: Autonomous Engineering Council (AI Doc Agent)

</div>

---

## Overview
The AI Doc Agent is an autonomous architectural review tool serving the Sentinel platform. It acts as an automated engineering council by analyzing git history and line-by-line diffs over a specified timeframe to generate a comprehensive, persona-driven weekly report.

## Architecture & Workflow
*   **Dynamic Personas:** Automatically assigns expert roles (e.g., Zero-Trust Security Architect, Senior Cloud/DevOps Engineer, Lead Data Scientist) based on the specific file paths modified in the commit history.
*   **State Management:** Reads the most recent weekly report before generating a new one to track technical debt, ensuring continuity and follow-up on unresolved architectural issues.
*   **Hallucination Prevention:** Enforces strict Large Language Model constraints (low temperature) and automatically aborts execution if the git diff lacks significant architectural changes.
*   **Fail-Fast Architecture:** Validates the presence of required environment variables prior to execution, providing actionable Developer Experience (DevEx) feedback if missing.

## Prerequisites
Ensure the following tools and configurations are present before running the agent:
*   **[Taskfile](https://taskfile.dev/installation/):** Task runner
*   **[uv](https://github.com/astral-sh/uv):** Python package manager
*   **Gemini API Key:** Required for the LLM engine to function

## Quick Start & Usage
The agent is seamlessly integrated into the project's native task runner and automatically loads local `.env` configurations.

To trigger the weekly architectural review, execute:
```bash
task agent:doc
```

## Configuration & Environment
The agent relies on local environment variables and generates local artifacts.

| Key / Artifact | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Must be defined in the `.env` file for API authentication. |
| `weekly_report_*.md` | The agent generates a timestamped markdown report (e.g., `weekly_report_YYYY-MM-DD.md`) within this directory. |

> **Note:** To maintain repository hygiene and prevent bloat, these generated operational reports are explicitly ignored by version control (`.gitignore`) and remain strictly local to the execution environment.
