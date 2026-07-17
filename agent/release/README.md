# Release Automation Agent (AI-Powered)

The Release Agent is an autonomous, AI-driven Python script designed to eliminate the toil of manual versioning and changelog generation. By analyzing Git commit histories and raw code diffs, it dynamically calculates the next Semantic Version (SemVer) and leverages the Gemini API to write human-readable, business-focused release notes.

## Key Features

- **Autonomous SemVer Calculation:** Automatically analyzes commit conventions (e.g., `feat:`, `fix:`, `breaking change!`) to determine if the next release requires a `MAJOR`, `MINOR`, or `PATCH` bump.
- **AI-Generated Release Notes:** Uses the `gemini-2.5-flash-lite` model via the Google GenAI SDK to translate raw `git diff` and commit messages into structured, architectural-level release documentation.
- **Resilient API Handling:** Implements an intelligent retry and exponential backoff mechanism with Regex-based parsing to handle API rate limits (HTTP 429) or transient errors gracefully.
- **CI/CD Integration:** Automatically updates the `CHANGELOG.md` and exports the dynamically generated `NEXT_TAG` to the `$GITHUB_ENV` for downstream GitHub Action release pipelines.

## How It Works

1. **Tag Discovery:** Queries Git for the latest release tag (`git describe`).
2. **Context Gathering:** Extracts all commit messages and the exact code differences (`git diff`) since the last tag.
3. **Prompt Engineering:** Passes the data to the AI with strict system instructions to focus on *engineering value* and *architectural trade-offs* rather than mundane syntax changes.
4. **Documentation Sync:** Prepends the AI-generated markdown to `CHANGELOG.md` and prepares the environment for the Git push.

## Quick Start (Local Run)

Ensure you have your Gemini API key configured:

```bash
export GEMINI_API_KEY="your_api_key_here"
uv run release_agent.py
```

### Example AI Output Structure

The agent strictly adheres to the following generation format:

* **Changed Files & Core Modifications:** High-level summary of what was altered.
* **Reason for Changes:** The underlying issue or business requirement.
* **Advantages & Architectural Trade-offs:** Detailed pros (e.g., lower latency) and cons (e.g., deprecations).
