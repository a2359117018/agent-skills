# Exit Codes Reference

`describe.py` normalizes all output. On success (exit code 0), stdout is plain-text content.
On failure (non-zero), stdout is JSON with `error` and `message` fields.

| Exit code | Error                 | When                                              |
| --------- | --------------------- | ------------------------------------------------- |
| 0         | _(success)_           | Image analyzed successfully                       |
| 1         | `CLI_NOT_FOUND`       | `mmx` not installed or not on PATH               |
| 2         | `AUTH_NOT_CONFIGURED` | API key missing, invalid, or expired              |
| 3         | `CLI_ERROR`           | File not found, unsupported format, JSON parse failure |
| 4         | `API_ERROR`           | `base_resp.status_code` non-zero (API-side error) |

## Common Scenarios

- **Exit 1**: Install mmx CLI (`npm install -g minimax-cli`)
- **Exit 2**: Run `mmx auth` or set `MINIMAX_API_KEY` environment variable
- **Exit 3**: Check file path exists and extension is `.jpg/.jpeg/.png/.webp`
- **Exit 4**: Verify API key is valid and not expired; check network connectivity
