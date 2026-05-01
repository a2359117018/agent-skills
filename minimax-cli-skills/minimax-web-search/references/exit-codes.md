# Exit Codes Reference

`search.py` normalizes all output. On success (exit code 0), stdout is JSON with a `results` array.
On failure (non-zero), stdout is JSON with `error` and `message` fields.

| Exit code | Error                 | When                                              |
| --------- | --------------------- | ------------------------------------------------- |
| 0         | _(success)_           | Search completed, results returned (may be empty) |
| 1         | `CLI_NOT_FOUND`       | `mmx` not installed or not on PATH               |
| 2         | `AUTH_NOT_CONFIGURED` | API key missing or not configured                 |
| 3         | `CLI_ERROR`           | CLI execution failure or JSON parse error         |
| 4         | `API_ERROR`           | `base_resp.status_code` non-zero (API-side error) |

## Common Scenarios

- **Exit 1**: Install mmx CLI (`npm install -g minimax-cli`)
- **Exit 2**: Run `mmx auth` or set `MINIMAX_API_KEY` environment variable
- **Exit 3**: Check mmx CLI version; verify network connectivity; retry with a simpler query
- **Exit 4**: Verify API key is valid and not expired; check if search quota is exhausted
