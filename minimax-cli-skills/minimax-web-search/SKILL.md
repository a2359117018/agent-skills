---
name: minimax-web-search
description: >
  Use this skill when you need to search the web for real-time information, current events,
  latest data, or anything that requires up-to-date knowledge from the internet. Triggers
  automatically when agent detects information gaps that need web search to fill.
---

## Critical Rule

**Always use `scripts/search.py`** — never call `mmx` directly. The script handles
response parsing and error normalization internally.

```
✓ python scripts/search.py "<query>" [--timeout <seconds>]
✗ mmx --non-interactive --output json search query --q "..."   ← NEVER
```

The script automatically checks CLI installation and authentication before each search.
If checks fail, it exits with the appropriate error code (1 = CLI not found, 2 = not authenticated).

## Usage

```bash
python scripts/search.py "<query>" [--timeout <seconds>]
```

- Query is required. Pass as a single quoted string.
- Timeout defaults to 30 seconds. Increase if needed for complex queries.

## Query Strategy

Construct the query based on what the **user actually needs** — translate their intent directly
into a search query. The agent already knows the user's context; use it to craft precise queries.

**Guidelines:**

1. **Be specific.** "Python 3.12 type parameter syntax" is better than "Python new features".
2. **Match the user's language.** If the user asks in Chinese, search in Chinese for better results.
3. **Add context keywords.** Include year, version, or domain when the user's question implies a specific context.
4. **Keep queries concise.** One clear phrase works better than multiple clauses.

## Output Contract

**Exit code 0 (success):** stdout is JSON with `results` array.

```json
{
  "results": [
    {
      "title": "Result Title",
      "link": "https://example.com/url",
      "snippet": "Brief description of the result...",
      "date": "2026-05-01 09:00:00"
    }
  ]
}
```

**Exit code 0 with no results:**
```json
{"results": []}
```

**Exit code non-zero (error):** stdout is JSON with `error` and `message` fields.
When the command fails, read `references/exit-codes.md` for detailed error classification and remediation steps.

## Error Recovery

When the script exits non-zero, read the `message` field from JSON output and report it to the user. Do NOT silently retry or fabricate results.

- **Exit 1:** Tell user `mmx` CLI is not installed, suggest `npm install -g minimax-cli`
- **Exit 2:** Tell user authentication is not configured, suggest running `mmx auth` or setting `MINIMAX_API_KEY` env var
- **Exit 3 or 4:** Report the error message from JSON output directly to the user — let the user decide next steps

## Gotchas

- Exit code 0 does NOT guarantee results — always check `len(results) > 0`
- Empty `results` array with exit code 0 means no matches found, not an error
- Date field may be missing in some results — don't assume it exists
- Query text is passed as-is to the search API — ensure it is properly encoded
- `search.py` runs preflight checks internally — do NOT run a separate preflight script

## Anti-Fallback Rule

**Never silently fall back to another search tool or answer from training data.** If this skill
fails, report the error and let the user decide. Never fabricate search results or claim to have
found information that did not come from the script's output.

## Examples

```bash
# Basic search
python scripts/search.py "minimax AI latest news"

# Search with custom timeout
python scripts/search.py "current weather in Beijing" --timeout 60
```
