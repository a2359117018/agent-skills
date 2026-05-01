---
name: minimax-vision-describe
description: >
  Use this skill when you need to understand what is in an image — describe content, extract text
  (OCR), analyze screenshots, read diagrams, or identify UI elements. Applies to local image files
  (*.jpg, *.jpeg, *.png, *.webp) and image URLs. Trigger even if the user doesn't explicitly mention
  "image analysis" — any task that requires knowing what a picture shows should use this skill first.
---

## Critical Rule & Usage

**Always use `scripts/describe.py`** — never call `mmx` directly. The script handles preflight checks,
authentication, response parsing, and error normalization internally.

```bash
# Correct
python scripts/describe.py <image-path> [--prompt "<instruction>"] [--timeout <seconds>]

# Wrong — NEVER do this
mmx vision describe --image "..."
```

- Image path is required. Local file (`.jpg`, `.jpeg`, `.png`, `.webp`) or HTTP(S) URL.
- `-p/--prompt` is optional. Omit for a default description; provide it when you have a specific
  extraction goal (OCR, components, errors, layout, colors, etc.).
- `-t/--timeout` is optional (default 120s). Increase for large images.

**Security:** Never log, display, or persist the full API key value.

## Gotchas

- `describe.py` runs preflight internally — do NOT run `preflight.py` separately.
- Preflight checks key existence from `auth status`, not validity. An expired/revoked key may pass preflight
  but fail at the API call with `API_ERROR`.
- On Windows, the script uses `shell=True` internally to resolve `.cmd` wrappers — no action needed.

## Prompt Strategy

Construct the `--prompt` argument based on what the **user actually asked for** — do not classify the image
into a fixed type first. The agent already knows the user's intent; translate that intent directly into a
specific vision prompt.

**Guidelines for effective prompts:**

1. **Be specific about the extraction goal.** Tell the vision model exactly what to focus on — text only,
   structural relationships, visual elements, colors, etc.
2. **Specify output format when useful.** Mention ordering, numbering, bullet points, or hierarchical
   structure if the user cares about presentation.
3. **Match the user's language.** If the user asks in Chinese, craft the prompt in Chinese or bilingual
   to ensure the response is in the expected language.
4. **Omit `--prompt` for general description.** When the user just wants to "see what's in the image",
   let the script use its default behavior without a custom prompt.

**Examples** (for reference — adapt to the actual request, do not copy verbatim):

- User asks "what's in this diagram" → `--prompt "Describe all visual elements, their labels, and how they connect"`
- User asks "extract the text" → `--prompt "Extract all visible text exactly, preserving order and numbering"`
- User asks "is there an error?" → `--prompt "Identify any error messages, stack traces, or warning indicators"`
- User asks "what colors are used" → `--prompt "List all distinct colors and which elements they apply to"`

## Output Contract

**Exit code 0 (success):** stdout is plain-text content describing the image, prefixed with
`(Image analysis)`. Incorporate this prefix into your response rather than stripping it.

- User asked a direct question → use content as primary source. May summarize or restructure, but must
  not contradict the vision output.
- Agent discovered an image during repo reading → extract structured info (component names, text labels,
  architecture relationships) into the ongoing task.
- OCR task → extract raw text verbatim. Preserve original ordering and numbering.

**Exit code non-zero (error):** stdout is JSON with `error` and `message` fields. When the command fails,
read `references/exit-codes.md` for detailed error classification and remediation steps.

**Never silently fall back to another vision tool.** If this skill fails, report the error and let the
user decide. Never fabricate image content or answer from the agent's own knowledge about what the image
"probably" contains.
