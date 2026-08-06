<div align="left">

# Sentinel: Enterprise Real-Time Fraud & Anomaly Ingestion Engine
### Module: Release Automation Agent (AI-Powered)

</div>

---

## Overview
The Release Agent is an autonomous, AI-driven Python engine designed to eliminate the toil of manual versioning and changelog generation. By analyzing Git commit histories and raw code diffs, it dynamically calculates the next Semantic Version (SemVer) and leverages the Gemini API to write human-readable, business-focused release notes.

## Architecture & Workflow

### Core Mechanisms
*   **Strict SemVer Calculation:** Automatically and strictly analyzes Git commit conventions (e.g., `feat:`, `fix:`, `breaking change!`) to determine if the next release requires a `MAJOR`, `MINOR`, or `PATCH` bump, ensuring rigorous adherence to semantic versioning standards.
*   **Nightly CI/CD Automation:** Fully integrated into the CD pipeline, the agent runs autonomously every night at 02:00 AM via a cron schedule. It evaluates daily changes, updates `CHANGELOG.md`, and exports the dynamically generated `NEXT_TAG` to the `$GITHUB_ENV` for downstream GitHub Release creation.
*   **AI-Generated Documentation:** Uses the `gemini-2.5-flash-lite` model via the Google GenAI SDK to translate raw `git diff` data and commit messages into structured, architectural-level release documentation.
*   **Resilient API Handling:** Implements an intelligent retry and exponential backoff mechanism with Regex-based parsing to handle API rate limits (HTTP 429) or transient network errors gracefully.

### Execution Flow
1.  **Tag Discovery:** Queries Git for the latest release tag (`git describe`).
2.  **Context Gathering:** Extracts all commit messages and the exact code differences (`git diff`) since the last tag.
3.  **Prompt Engineering:** Passes the data to the AI with strict system instructions to focus on *engineering value* and *architectural trade-offs* rather than mundane syntax changes.
4.  **Documentation Sync:** Prepends the structured AI output to `CHANGELOG.md`.

### AI Output Structure
The generated release notes strictly adhere to the following format:
*   **Changed Files & Core Modifications:** High-level summary of what was altered.
*   **Reason for Changes:** The underlying issue or business requirement.
*   **Advantages & Architectural Trade-offs:** Detailed pros (e.g., lower latency) and cons (e.g., deprecations).

## Prerequisites
Ensure the following tools and configurations are present before running the agent locally:
*   **[uv](https://github.com/astral-sh/uv):** Ultra-fast Python package installer and resolver.
*   **Gemini API Key:** Required for the LLM inference engine.
*   **Git:** Local repository must have at least one previous tag (e.g., `v1.0.0`) for delta calculation.

## Quick Start & Usage
While this agent is designed to run autonomously within GitHub Actions, it can be executed manually for local dry-runs and testing.

```bash
# 1. Export your Gemini API Key
export GEMINI_API_KEY="your_api_key_here"

# 2. Execute the release agent via uv
uv run release_agent.py
```

## Configuration & Environment
The agent relies on specific environment variables and interacts with the repository's root changelog.

| Key / File | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Must be defined in the environment for API authentication. |
| `CHANGELOG.md` | The target markdown file that the agent dynamically updates. |
| `NEXT_TAG` | (CI/CD only) Exported to `$GITHUB_ENV` to instruct downstream jobs on which tag to publish. |
