---
name: minimax-vision-describe
description: >
  Use this skill when you need to understand what is in an image — describe content, extract text
  (OCR), analyze screenshots, read diagrams, or identify UI elements. Applies to local image files
  (*.jpg, *.jpeg, *.png, *.webp) and image URLs. Trigger even if the user doesn't explicitly mention
  "image analysis" — any task that requires knowing what a picture shows should use this skill first.
---

## When to Use

Use this skill when you need to understand what is in an image:

1. The user provides an image and asks a question about it.
2. You encounter image files (`*.jpg`, `*.jpeg`, `*.png`, `*.webp`) in the repository and need their
   content to continue your task.
3. You need to perform OCR, visual analysis, or extract information from a screenshot, diagram, or
   mockup.

## When NOT to Use

- Image generation or editing
- Video analysis
- Batch processing of large image sets
- Real-time streaming analysis

## Critical Rule

**Always use `scripts/describe.ps1`** — never call `mmx` directly. The script handles preflight checks,
authentication, response parsing, and error normalization internally.

```
✓ powershell -ExecutionPolicy Bypass -File "scripts/describe.ps1" -Image "..." -Prompt "..."
✗ mmx vision describe --image "..."            ← NEVER
```

**Security:** Never log, display, or persist the full API key value.

## Gotchas

- `describe.ps1` runs preflight internally — do NOT run `preflight.ps1` separately.
- Preflight checks key existence (`$auth.key`), not validity. An expired/revoked key may pass preflight
  but fail at the API call with `API_ERROR`.
- The script has a `-TimeoutSeconds` parameter (default 120s). Increase it for large images:

  ```bash
  powershell -ExecutionPolicy Bypass -File "scripts/describe.ps1" -Image "huge.png" -TimeoutSeconds 300
  ```

- Windows paths with spaces must be wrapped in double quotes.
- `-Prompt` is passed as a PowerShell parameter — avoid unescaped double quotes inside the prompt text.

## Usage

```bash
powershell -ExecutionPolicy Bypass -File "scripts/describe.ps1" -Image "<path-or-url>" [-Prompt "<instruction>"]
```

- `-Image` is required. Local file path (`.jpg`, `.jpeg`, `.png`, `.webp`) or HTTP(S) URL.
- `-Prompt` is optional. Omit for a default description; provide it when you have a specific extraction
  goal (OCR, components, errors, layout).

## Prompt Strategy

| Image type           | Example prompt                                                              |
| -------------------- | --------------------------------------------------------------------------- |
| Architecture diagram | "Summarize the architecture layers, key components, and data flow. List unknown labels." |
| Product spec image   | "Extract requirements, acceptance criteria, and constraints as bullet points."            |
| Screenshot QA        | "Describe visible UI states and identify potential interaction issues."                   |
| OCR focus            | "Only extract all visible text exactly, preserving order and key numbering."              |
| UI mockup            | "List all UI components, their layout relationships, and interactive elements."           |
| Error screenshot     | "Extract the error message, stack trace, and surrounding context."                        |

## Output Contract

`describe.ps1` normalizes all output. Interpret the result by exit code:

**Exit code 0 (success):** stdout is plain-text content describing the image.

- User asked a direct question → use content as primary source. May summarize or restructure, but must
  not contradict the vision output.
- Agent discovered an image during repo reading → extract structured info (component names, text labels,
  architecture relationships) into the ongoing task.
- OCR task → extract raw text verbatim. Preserve original ordering and numbering.
- Indicate the information came from image analysis (e.g., "Based on the image analysis, ...").

**Exit code non-zero (error):** stdout is JSON with `error` and `message` fields.

| Exit code | Error                 | When                                |
| --------- | --------------------- | ----------------------------------- |
| 1         | `CLI_NOT_FOUND`       | `mmx` not installed                 |
| 2         | `AUTH_NOT_CONFIGURED` | API key missing or invalid          |
| 3         | `CLI_ERROR`           | CLI execution or JSON parse failure |
| 4         | `API_ERROR`           | `base_resp.status_code` non-zero    |

**Never silently fall back to another vision tool.** If this skill fails, report the error and let the
user decide. Never fabricate image content or answer from the agent's own knowledge about what the image
"probably" contains.

## Examples

```bash
# Architecture diagram analysis
powershell -ExecutionPolicy Bypass -File "scripts/describe.ps1" `
  -Image "f:/data/demo.png" `
  -Prompt "Summarize architecture components and interactions"

# Remote URL with requirements extraction
powershell -ExecutionPolicy Bypass -File "scripts/describe.ps1" `
  -Image "https://example.com/demo.jpg" `
  -Prompt "Extract product requirements and key constraints"

# Default description (no prompt)
powershell -ExecutionPolicy Bypass -File "scripts/describe.ps1" `
  -Image "./screenshots/homepage.png"
```
