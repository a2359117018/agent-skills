#!/usr/bin/env python
"""
Web search using minimax-cli mmx command.
Handles preflight checks, execution, response parsing, and error normalization.
Exit codes: 0=success, 1=CLI_NOT_FOUND, 2=AUTH_NOT_CONFIGURED, 3=CLI_ERROR, 4=API_ERROR
"""

import json
import logging
import re
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from dataclasses import dataclass

_IS_WINDOWS = sys.platform == "win32"

REQUIRED_FIELDS = ["title", "link", "snippet"]

logger = logging.getLogger(__name__)


@dataclass
class CLIResult:
    returncode: int
    stdout: str
    stderr: str


def run_command(cmd, timeout=30):
    """Run a command list and return a CLIResult.

    On Windows, mmx is typically installed as a .cmd/.ps1 script which cannot
    be executed directly by CreateProcess.  We therefore pass ``shell=True``
    on Windows so cmd.exe handles the script resolution.  When shell=True,
    we build the command string via list2cmdline and escape ``%`` to ``%%``
    to prevent cmd.exe environment-variable expansion in arguments.
    """
    try:
        if _IS_WINDOWS:
            cmdline = subprocess.list2cmdline(cmd).replace("%", "%%")
            proc = subprocess.run(
                cmdline,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                shell=True,
            )
        else:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        return CLIResult(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    except subprocess.TimeoutExpired:
        return CLIResult(returncode=-1, stdout="", stderr=f"Command timed out after {timeout}s")
    except (OSError, subprocess.SubprocessError) as e:
        return CLIResult(returncode=-1, stdout="", stderr=str(e))


def check_cli_installed():
    """Check if mmx CLI is available on PATH."""
    return shutil.which("mmx") is not None


def check_auth():
    """Check if user is authenticated. Returns (is_authenticated, error_message)."""
    result = run_command(
        ["mmx", "--non-interactive", "--output", "json", "auth", "status"],
        timeout=30,
    )

    if result.returncode != 0:
        return False, result.stderr or "Unknown auth error"

    try:
        data = json.loads(result.stdout)
        if data.get("method") and data.get("key"):
            return True, None
        return False, "No API key found. Run 'mmx auth' or set MINIMAX_API_KEY"
    except json.JSONDecodeError:
        return False, "Failed to parse auth response"


def clean_json_string(s):
    """Remove invalid control characters from JSON string but preserve newlines."""
    return re.sub(r"[\x00-\x09\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", s)


def validate_result(result):
    """Validate that a result has all required fields. Returns (is_valid, missing_fields)."""
    missing = [f for f in REQUIRED_FIELDS if f not in result or not result[f]]
    return len(missing) == 0, missing


def run_search(query, timeout=30):
    """Execute mmx search command and return parsed results."""
    cmd = [
        "mmx", "--non-interactive", "--output", "json",
        "search", "query", "--q", query,
    ]

    logger.debug("Running: %s", " ".join(cmd))
    result = run_command(cmd, timeout=timeout)

    if result.returncode != 0:
        return {"error": "CLI_ERROR", "message": result.stderr or "Unknown CLI error", "exit_code": 3}

    if not result.stdout.strip():
        return {"error": "CLI_ERROR", "message": "No output from mmx command", "exit_code": 3}

    cleaned = clean_json_string(result.stdout)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            return {"error": "CLI_ERROR", "message": f"Failed to parse JSON: {e}", "exit_code": 3}

    base_resp = data.get("base_resp", {})
    if base_resp.get("status_code", -1) != 0:
        return {
            "error": "API_ERROR",
            "message": base_resp.get("status_msg", "API returned non-zero status"),
            "exit_code": 4,
        }

    organic = data.get("organic", [])
    if not organic:
        return {"results": [], "exit_code": 0}

    validated_results = []
    warnings = []
    for idx, item in enumerate(organic):
        is_valid, missing = validate_result(item)
        if is_valid:
            validated_results.append(item)
        else:
            warnings.append(f"Result {idx} missing required fields: {missing}")

    return {"results": validated_results, "exit_code": 0, "warnings": warnings}


def print_error(error_code, message):
    """Print error JSON and exit with code."""
    error_map = {
        1: "CLI_NOT_FOUND",
        2: "AUTH_NOT_CONFIGURED",
        3: "CLI_ERROR",
        4: "API_ERROR",
    }
    print(json.dumps({"error": error_map.get(error_code, "UNKNOWN"), "message": message}))
    sys.exit(error_code)


def main():
    parser = ArgumentParser(description="Web search using minimax-cli")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Timeout in seconds (default: 30)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    if not check_cli_installed():
        print_error(1, "mmx is not installed or not on PATH")

    is_auth, auth_error = check_auth()
    if not is_auth:
        print_error(2, auth_error)

    logger.debug("Searching for: %s", args.query)
    result = run_search(args.query, args.timeout)

    if "error" in result:
        print_error(result["exit_code"], result["message"])

    print(json.dumps({"results": result["results"]}))
    if result.get("warnings"):
        for w in result["warnings"]:
            print(w, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
