import os
import re
import subprocess  # nosec B404
import sys
import time

from google import genai
from google.genai import types


def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)  # nosec B602
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e.stderr}", file=sys.stderr)
        return None


def get_latest_tag():
    tag = run_command("git describe --tags --abbrev=0")
    return tag if tag else "v0.0.0"


def get_commit_messages(latest_tag):
    if latest_tag == "v0.0.0":
        command = "git log --pretty=format:'%s'"
    else:
        command = f"git log {latest_tag}..HEAD --pretty=format:'%s'"
    commits = run_command(command)
    return commits.split("\n") if commits else []


def get_git_diff(latest_tag, max_chars=40000):
    # Exclude lock files and generated assets to save input tokens
    exclude_pattern = "-- . ':!*lock*' ':!*.json' ':!*.min.*' ':!*.svg' ':!*.csv'"
    if latest_tag == "v0.0.0":
        command = f"git diff $(git hash-object -t tree /dev/null) HEAD {exclude_pattern}"
    else:
        command = f"git diff {latest_tag} HEAD {exclude_pattern}"

    diff = run_command(command)
    if not diff:
        return ""

    if len(diff) > max_chars:
        return diff[:max_chars] + "\n\n[Diff truncated to stay within model token quotas...]"
    return diff


def analyze_semver_bump(commit_messages):
    bump = "SKIP"

    commit_pattern = re.compile(r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[a-zA-Z0-9_\-]+)\))?(?P<breaking>!)?:")

    for msg in commit_messages:
        msg_clean = msg.strip()

        if "BREAKING CHANGE" in msg_clean:
            return "MAJOR"

        match = commit_pattern.match(msg_clean)

        if not match:
            if bump == "SKIP" and msg_clean:
                bump = "PATCH"
            continue

        commit_type = match.group("type").lower()
        is_breaking = bool(match.group("breaking"))

        if is_breaking:
            return "MAJOR"

        if commit_type == "feat":
            if bump in ["SKIP", "PATCH"]:
                bump = "MINOR"

        elif commit_type in ["fix", "perf", "refactor", "revert", "style"]:
            if bump == "SKIP":
                bump = "PATCH"

        elif commit_type in ["chore", "docs", "ci", "test", "build"]:
            pass

        else:
            if bump == "SKIP":
                bump = "PATCH"

    return bump


def bump_version(current_version, bump_type):
    version_str = current_version.lstrip("v")
    major, minor, patch = map(int, version_str.split("."))

    if bump_type == "MAJOR":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "MINOR":
        minor += 1
        patch = 0
    elif bump_type == "PATCH":
        patch += 1

    return f"v{major}.{minor}.{patch}"


def generate_release_notes(next_version, commit_messages, git_diff):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[CRITICAL] GEMINI_API_KEY environment variable not found.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    system_instruction = (
        "You are a Principal Platform Engineer responsible for writing clear, concise, and professional release notes. "
        "Your audience includes other engineers, DevOps practitioners, and stakeholders. "
        "Analyze the commit messages and git diff to explain 'what' changed and 'why' it matters. "
        "Do NOT provide code review feedback, security fix suggestions, or mention minor syntax changes. "
        "Focus purely on the architectural and functional value delivered in this release."
    )

    prompt = f"""
Generate structured release notes for version **{next_version}**.

### Input Data:
1. **Commit Logs:**
{chr(10).join(commit_messages)}

2. **Raw Git Diff:**
{git_diff}

### Target Markdown Template Structure:
Please strictly fill out the following template. Omit empty sections. Do not hallucinate metrics.

### {next_version}

#### 🚀 Features & Core Modifications
- Summarize the main engineering changes and new capabilities.

#### 🛠 Stability & Performance (Fixes)
- Mention resolved technical debt, bug fixes, or performance improvements.

#### 🏗 Architectural Impact
- Note any changes to deployment, infrastructure requirements, or potential breaking changes.
"""

    max_retries = 3
    retry_delay = 60

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                ),
            )
            return response.text
        except Exception as e:
            err_msg = str(e)
            if (
                "503" in err_msg or "UNAVAILABLE" in err_msg or "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg
            ) and attempt < max_retries - 1:
                print(
                    f"Rate limit or temporary API error encountered. Waiting {retry_delay}s before retry ({attempt + 1}/{max_retries})...",
                    file=sys.stderr,
                )
                time.sleep(retry_delay)
                continue
            return f"Failed to generate release notes via Gemini API: {err_msg}"


if __name__ == "__main__":
    print("Release Agent is initializing...")

    current_tag = get_latest_tag()
    print(f"Current Latest Version: {current_tag}")

    commits = get_commit_messages(current_tag)
    if not commits or commits == [""]:
        print("No new commits found. Exiting.")
        sys.exit(0)

    bump_decision = analyze_semver_bump(commits)
    print(f"SemVer Analysis Result: {bump_decision}")

    if bump_decision == "SKIP":
        print("Only non-release commits (chore, docs, ci, test) found. Skipping release generation.")
        sys.exit(0)

    next_tag = bump_version(current_tag, bump_decision)
    print(f"Proposed New Version: {next_tag}")

    diff_data = get_git_diff(current_tag)

    print("Invoking Gemini AI for Release Notes...")
    release_notes = generate_release_notes(next_tag, commits, diff_data)

    if release_notes.startswith("Failed to generate"):
        print(f"CRITICAL ERROR: {release_notes}")
        sys.exit(1)

    with open("release_notes.md", "w", encoding="utf-8") as f:
        f.write(release_notes)

    changelog_path = "CHANGELOG.md"
    existing_content = ""

    if os.path.exists(changelog_path):
        with open(changelog_path, encoding="utf-8") as f:
            existing_content = f.read()
    else:
        existing_content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n"

    new_changelog = f"{release_notes}\n\n---\n\n{existing_content}"

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(new_changelog)

    if "GITHUB_ENV" in os.environ:
        with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as env_file:
            env_file.write(f"NEXT_TAG={next_tag}\n")
