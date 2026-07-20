import glob
import os
import re
import subprocess  # nosec B404
import sys
import time
from datetime import datetime

from google import genai
from google.genai import types


def run_command(command):
    try:
        result = subprocess.run(  # nosec B602
            command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True, shell=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e.stderr}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error: {e!s}", file=sys.stderr)
        return None


def get_git_data(timeframe="1 weeks ago"):
    log_command = f'git log --since="{timeframe}" --pretty=format:"%s"'
    log_data = run_command(log_command)

    if not log_data:
        return None, None

    hash_command = f'git log --since="{timeframe}" --reverse --format="%H"'
    hashes = run_command(hash_command)

    if not hashes:
        return None, None

    first_commit = hashes.split("\n")[0].strip()

    diff_command = (
        f'git diff {first_commit}~1 HEAD -- . ":(exclude)*.lock" ":(exclude)go.sum" ":(exclude)docs/images/*"'
    )
    diff_data = run_command(diff_command)

    if diff_data is None:
        diff_command = (
            f'git diff {first_commit} HEAD -- . ":(exclude)*.lock" ":(exclude)go.sum" ":(exclude)docs/images/*"'
        )
        diff_data = run_command(diff_command)

    return diff_data, log_data


def get_previous_report(directory="agent/doc"):
    search_pattern = os.path.join(directory, "weekly_report_*.md")
    existing_reports = sorted(glob.glob(search_pattern))

    if not existing_reports:
        return "No previous report found. This is the first run."

    latest_report_path = existing_reports[-1]
    print(f"Found previous state: Loading {latest_report_path} into memory...")

    with open(latest_report_path, encoding="utf-8") as f:
        return f.read()


def determine_personas(diff_data):
    personas = set()
    if not diff_data:
        return ["Technical Writer"]

    if re.search(r"b/src/(data|features|models|utils)/", diff_data):
        personas.add("Lead Data Scientist (focusing on feature engineering, MLOps constraints, and inference logic)")

    if re.search(
        r"b/(infrastructure/.*\.(tf|yaml|yml)|Dockerfile.*|\.github/workflows/.*|Jenkinsfile|docker-compose.*)",
        diff_data,
    ):
        personas.add(
            "Senior Cloud/DevOps Engineer (focusing on CI/CD pipeline robustness, container security, and FinOps)"
        )

    if re.search(r"b/policy/.*\.rego", diff_data):
        personas.add("Zero-Trust Security Architect (focusing on Policy-as-Code and cluster governance)")

    if re.search(r"b/.*\.go", diff_data):
        personas.add("Staff Go Backend Engineer (focusing on concurrent throughput and API latency)")

    if re.search(r"b/.*\.rs", diff_data):
        personas.add("Systems Rust Engineer (focusing on memory safety and ultra-low latency execution)")

    if re.search(r"b/.*\.md", diff_data):
        personas.add(
            "Staff Technical Writer (focusing on architectural alignment in documentation and clear API contracts)"
        )

    if len(personas) > 1:
        personas.add("Principal Tech Lead (orchestrating cross-domain architectural decisions and resolving conflicts)")
    elif len(personas) == 0:
        personas.add("Senior Software Engineer")

    return list(personas)


def generate_weekly_report(diff_data, log_data, previous_report, personas):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("CRITICAL: GEMINI_API_KEY environment variable not found.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    persona_string = ", ".join(personas)
    today_str = datetime.now().strftime("%Y-%m-%d")

    system_instruction = (
        f"You are the autonomous Engineering Council composed of: {persona_string}. "
        "Analyze the Git logs and Git diff to generate a strictly segmented architectural review. "
        "STRICT RULES TO PREVENT HALLUCINATIONS: "
        f"1. NEVER invent or hallucinate dates. You must use the exact date provided: {today_str}. "
        "2. NEVER invent dummy data like 'Issue X' or 'Issue Y'. If the provided diff lacks significant architectural changes, explicitly state 'No significant architectural changes found' for that department. "
        "3. If the 'Previous Week's Report' states 'No previous report found', explicitly skip the tracking section. "
        "4. Filter out mundane typo fixes. Output must be strictly professional English, no emojis, in Markdown."
    )

    prompt = f"""
Generate the weekly architectural review.

### 1. Previous Week's Report (For Context & Tracking):
{previous_report}

### 2. This Week's Git Logs:
{log_data}

### 3. This Week's Raw Git Diff:
{diff_data}

### Mandatory Output Structure:
# Weekly Engineering Council Report - {today_str}

## 1. Context & Continuity
* Address issues from the Previous Week's Report. If no previous report exists, state "Initial baseline report."

## 2. Departmental Reviews
Segment the architectural changes and vulnerabilities ([CRITICAL], [HIGH], [MEDIUM], [LOW]) into the following departments based on the diff. If a department had no changes, explicitly write "No significant changes."
* **Infrastructure & CI/CD Desk:**
* **Core Backend & Concurrency:**
* **ML Pipeline & Data Science:**
* **Security & Policy Governance:**
* **Documentation & Developer Experience:**

## 3. Action Items for Next Week
* Provide up to 3 actionable, prioritized tasks for the engineering team. If the diff was empty, state "No critical actions derived from this week's commits."
"""

    print("Invoking AI context analysis...")

    max_retries = 4
    retry_delay = 30

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                ),
            )
            return response.text
        except Exception as e:
            print(f"API Error (Attempt {attempt + 1}/{max_retries}): {e!s}", file=sys.stderr)
            if attempt < max_retries - 1:
                print(f"Waiting {retry_delay} seconds before retrying...", file=sys.stderr)
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Context analysis failed.", file=sys.stderr)
                return None


if __name__ == "__main__":
    print("Initializing Autonomous Engineering Council (Doc Agent)...")

    if not os.environ.get("GEMINI_API_KEY"):
        print("[CRITICAL] GEMINI_API_KEY environment variable not found.", file=sys.stderr)
        print(
            "ACTION REQUIRED: Please create a '.env' file in the project root by copying '.env.example' and adding your API key.",
            file=sys.stderr,
        )
        sys.exit(1)

    diff_data, log_data = get_git_data("1 weeks ago")

    if not diff_data or len(diff_data.strip()) < 10:
        print("No significant changes found in the specified timeframe. Exiting to prevent AI hallucinations.")
        sys.exit(0)

    previous_report = get_previous_report("agent/doc")
    assigned_personas = determine_personas(diff_data)
    print(f"Dynamic Personas Assigned: {', '.join(assigned_personas)}")

    report_content = generate_weekly_report(diff_data, log_data, previous_report, assigned_personas)

    if report_content:
        os.makedirs("agent/doc", exist_ok=True)
        today_date = datetime.now().strftime("%Y-%m-%d")
        file_path = f"agent/doc/weekly_report_{today_date}.md"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Success: Weekly report generated at {file_path}")
    else:
        print("Failed to generate report.")
        sys.exit(1)
