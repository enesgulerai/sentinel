import os
import re
import subprocess
import sys
import time

from google import genai
from google.genai import types


def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
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


def get_git_diff(latest_tag):
    if latest_tag == "v0.0.0":
        command = "git diff $(git hash-object -t tree /dev/null) HEAD"
    else:
        command = f"git diff {latest_tag} HEAD"
    return run_command(command)


def analyze_semver_bump(commit_messages):
    bump = "PATCH"
    for msg in commit_messages:
        msg_clean = msg.lower()
        if "breaking change" in msg_clean or "!" in msg_clean.split(":")[0]:
            return "MAJOR"
        elif msg_clean.startswith("feat"):
            bump = "MINOR"
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
        print("Warning: GEMINI_API_KEY environment variable not found.", file=sys.stderr)
        return "Failed to generate: Missing API Key."

    client = genai.Client(api_key=api_key)

    system_instruction = (
        "You are an expert Release Automation Agent. Your task is to analyze the provided commit messages "
        "and line-by-line code differences (git diff). You must write professional, structured release notes.\n"
        "Do NOT mention internal variables, syntax details, or mundane structural changes unless they imply architectural impact. "
        "Focus on the 'Why' and the business/engineering value."
    )

    prompt = f"""
Generate release notes for version **{next_version}**.

### Input Data:
1. **Commit Logs:**
{chr(10).join(commit_messages)}

2. **Raw Git Diff:**
{git_diff}

### Target Markdown Template Structure:
Please strictly fill out the following template structure based on the inputs. If a section has no data, omit it or group it intelligently. Do not hallucinate metrics.

### {next_version}

#### Changed Files & Core Modifications
- Summarize what files changed and what was modified at a high engineering level.

#### Reason for Changes
- Explain the underlying issue or feature requirement that triggered these changes.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Mention improvements like lower latency, better isolation, resolved debt, etc.
- **(-) Disadvantages / Notes:** Mention any cost implications, potential deprecations, or infrastructure requirements.
"""

    max_retries = 5
    retry_delay = 10

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
                delay_match = re.search(r"retry in ([\d\.]+)s", err_msg)
                sleep_time = int(float(delay_match.group(1))) + 2 if delay_match else retry_delay * (attempt + 1)
                print(
                    f"API busy or rate-limited. Smart-sleeping for {sleep_time}s... (Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(sleep_time)
                continue
            return f"Failed to generate release notes via Gemini API: {err_msg}"


if __name__ == "__main__":
    print("Release Agent is initializing...")
    current_tag = get_latest_tag()
    print(f"Current Latest Version: {current_tag}")

    commits = get_commit_messages(current_tag)
    if not commits or commits == [""]:
        print("No new commits found. Release is not required.")
        sys.exit(0)

    print(f"Analyzed commit count: {len(commits)}")
    bump_decision = analyze_semver_bump(commits)
    print(f"SemVer Analysis Result: {bump_decision} bump required.")

    next_tag = bump_version(current_tag, bump_decision)
    print(f"Proposed New Version: {next_tag}")

    print("Gathering Git Diff and invoking Gemini AI for Release Notes...")
    diff_data = get_git_diff(current_tag)
    release_notes = generate_release_notes(next_tag, commits, diff_data)

    if release_notes.startswith("Failed to generate"):
        print(f"CRITICAL ERROR: {release_notes}")
        sys.exit(1)

    print("\n=================== GENERATED RELEASE NOTES ===================")
    print(release_notes)
    print("===============================================================")

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
