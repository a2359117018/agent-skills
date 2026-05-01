---
title: "refactor: Improve minimax-web-search to match project best practices"
type: refactor
status: active
date: 2026-05-01
---

# refactor: Improve minimax-web-search to match project best practices

## Overview

Refactor `minimax-web-search` skill to align with the established patterns in its sibling skill `minimax-vision-describe`, and address remaining best-practice gaps identified during review. The skill is functional and passes evals, but its script is Windows-only (PowerShell-coupled) and the directory structure is incomplete (missing `references/`).

## Problem Frame

The skill was reviewed against the project's best-practice guide. Two categories of issues were found:

1. **Script architecture** — `search.py` calls PowerShell explicitly (`run_powershell_simple`, `run_powershell_utf8`), making it Windows-only. The sibling `describe.py` demonstrates a cross-platform pattern using `shutil.which()` and `subprocess(shell=True on Windows)` that should be adopted.
2. **Directory structure** — AGENTS.md specifies `references/` for runtime reference material, and the sibling skill uses `references/exit-codes.md` for progressive disclosure. Web-search embeds this information inline in SKILL.md instead.

## Requirements Trace

- R1. `search.py` must be cross-platform (work on Windows, macOS, Linux)
- R2. `search.py` must follow the same architectural patterns as `describe.py` (CLIResult dataclass, logging, shutil.which, subprocess with shell flag)
- R3. Skill must have a `references/` directory with exit-code details, per AGENTS.md convention
- R4. SKILL.md must reference `references/exit-codes.md` via progressive disclosure instead of embedding the full table inline
- R5. All existing behavior must be preserved (same CLI interface, same JSON output contract, same exit codes)

## Scope Boundaries

- **Not changing** the description field (intentionally broad to capture all web-search triggers)
- **Not changing** evals (they are gitignored and out of scope)
- **Not adding** new scripts or features — this is a refactor, not feature work

## Context & Research

### Relevant Code and Patterns

- `minimax-cli-skills/minimax-vision-describe/scripts/describe.py` — reference implementation for cross-platform mmx wrapper script (CLIResult dataclass, `run_command` with `shell=_IS_WINDOWS`, `shutil.which`, logging)
- `minimax-cli-skills/minimax-vision-describe/references/exit-codes.md` — reference pattern for progressive disclosure of error codes
- `minimax-cli-skills/minimax-vision-describe/SKILL.md` — reference SKILL.md structure (Prompt Strategy section, "Never silently fall back" rule, references to exit-codes.md)
- `AGENTS.md` — project conventions (scripts/ dir, references/ dir, relative paths, no absolute paths)

## Key Technical Decisions

- **Adopt describe.py's subprocess pattern**: Replace `run_powershell_simple`/`run_powershell_utf8` with a single `run_command` function using `subprocess.run` and `shell=_IS_WINDOWS`. This is the proven pattern in this repo.
- **Replace fix_and_parse_json with clean_json_string**: The current `fix_and_parse_json` iterates character-by-character; describe.py's `clean_json_string` uses a simple regex. Both achieve the same goal; align to the simpler version.
- **Extract exit-code table to references/**: Move the detailed exit-code table out of SKILL.md into `references/exit-codes.md`, keeping only a brief summary in SKILL.md. This follows the progressive disclosure pattern recommended by both best practices and the sibling skill.

## Open Questions

### Resolved During Planning

- Cross-platform support: Confirmed — user wants cross-platform alignment with describe.py.

### Deferred to Implementation

- Exact prompt/wording adjustments in SKILL.md (minor copy editing during implementation)

## Implementation Units

- [ ] **Unit 1: Refactor search.py to cross-platform architecture**

**Goal:** Replace PowerShell-coupled code with the cross-platform pattern from describe.py.

**Requirements:** R1, R2, R5

**Dependencies:** None

**Files:**
- Modify: `minimax-cli-skills/minimax-web-search/scripts/search.py`

**Approach:**
- Remove `run_powershell_simple` and `run_powershell_utf8` functions
- Add `_IS_WINDOWS` flag, `CLIResult` dataclass, and `run_command` function (copy pattern from describe.py)
- Replace `check_cli_installed()` body with `shutil.which("mmx") is not None`
- Replace `check_auth()` to use `run_command` instead of `run_powershell_simple`
- Replace `run_search()` to use `run_command` instead of `run_powershell_utf8`
- Replace `fix_and_parse_json` with `clean_json_string` (regex-based, from describe.py)
- Remove unused imports (`re` becomes unused if adopting regex approach from describe.py — actually `clean_json_string` uses `re`, so keep it; remove `tempfile` which is unused)
- Add `logging` module and `--verbose` flag
- Keep the same `REQUIRED_FIELDS`, `validate_result`, `print_error`, and `main` logic
- Keep the same argparse interface (`query` positional, `--timeout` optional)

**Patterns to follow:**
- `minimax-cli-skills/minimax-vision-describe/scripts/describe.py` — the entire script structure (imports, dataclass, run_command, check_cli_installed, check_auth)

**Test scenarios:**
- Happy path: `python scripts/search.py "test query"` returns JSON with `results` array and exit code 0
- Edge case: Query with special characters (quotes, unicode) — verify escaping still works with the new subprocess approach
- Error path: `mmx` not installed — exit code 1 with `CLI_NOT_FOUND` JSON
- Error path: Not authenticated — exit code 2 with `AUTH_NOT_CONFIGURED` JSON
- Error path: API returns non-zero status — exit code 4 with `API_ERROR` JSON

**Verification:**
- Script runs identically on Windows (same JSON output, same exit codes)
- No PowerShell-specific code remains in the file

- [ ] **Unit 2: Add references/exit-codes.md**

**Goal:** Extract exit-code details from SKILL.md into a dedicated reference file for progressive disclosure.

**Requirements:** R3

**Dependencies:** None (can run in parallel with Unit 1)

**Files:**
- Create: `minimax-cli-skills/minimax-web-search/references/exit-codes.md`

**Approach:**
- Follow the exact structure of `minimax-vision-describe/references/exit-codes.md`
- Include the same exit code table (0–4) adapted for search context
- Include Common Scenarios section with remediation steps

**Patterns to follow:**
- `minimax-cli-skills/minimax-vision-describe/references/exit-codes.md`

**Test scenarios:**
- Test expectation: none — static reference document, verified by content review

**Verification:**
- File exists and covers all 5 exit codes (0–4)
- Remediation steps are accurate for search context

- [ ] **Unit 3: Update SKILL.md for progressive disclosure and query strategy**

**Goal:** Update SKILL.md to reference the new exit-codes file, add a query strategy section, and add an anti-fallback rule.

**Requirements:** R3, R4

**Dependencies:** Unit 2 (references/exit-codes.md must exist)

**Files:**
- Modify: `minimax-cli-skills/minimax-web-search/SKILL.md`

**Approach:**
- In the "Exit code non-zero" part of Output Contract, replace the inline table with a reference to `references/exit-codes.md`: "When the command fails, read `references/exit-codes.md` for detailed error classification and remediation steps."
- Keep the Error Recovery section in SKILL.md (it's actionable guidance, not reference material)
- Add a brief **Query Strategy** section (similar to vision-describe's Prompt Strategy) guiding the agent on how to construct effective search queries
- Add a **"Never silently fall back"** rule: if search fails, report the error; never fabricate results or answer from training data alone

**Patterns to follow:**
- `minimax-cli-skills/minimax-vision-describe/SKILL.md` — Output Contract references exit-codes.md; Prompt Strategy section; "Never silently fall back" rule

**Test scenarios:**
- Test expectation: none — SKILL.md is a static instruction document, verified by content review

**Verification:**
- SKILL.md references `references/exit-codes.md` for error details
- Query Strategy section is present and concise
- "Never silently fall back" rule is present
- Total SKILL.md stays under 120 lines

## System-Wide Impact

- **Interaction graph:** No callbacks, middleware, or observers affected. The script is a standalone CLI tool.
- **Error propagation:** Same exit codes, same JSON structure — no change to external contracts.
- **API surface parity:** No other interfaces consume search.py output beyond the agent reading stdout.
- **Unchanged invariants:** JSON output format, exit code values, CLI argument interface — all preserved.

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| Query escaping behavior changes when switching from PowerShell to subprocess | Test with special characters (quotes, unicode) before and after |
| JSON parsing regression if `clean_json_string` handles edge cases differently from `fix_and_parse_json` | Both functions strip control characters; verify with mmx's actual output |

## Sources & References

- Related code: `minimax-cli-skills/minimax-vision-describe/scripts/describe.py`
- Related code: `minimax-cli-skills/minimax-vision-describe/references/exit-codes.md`
- Related code: `minimax-cli-skills/minimax-vision-describe/SKILL.md`
- Project conventions: `AGENTS.md`
