import json, sys

print(json.dumps({"error": "CLI_NOT_FOUND", "message": "mmx is not installed or not on PATH"}))
sys.exit(1)
