import json, sys

print(json.dumps({"error": "CLI_ERROR", "message": "Command timed out after 30s"}))
sys.exit(3)
