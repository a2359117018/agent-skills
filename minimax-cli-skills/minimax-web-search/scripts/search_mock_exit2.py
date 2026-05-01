import json, sys

print(json.dumps({"error": "AUTH_NOT_CONFIGURED", "message": "No API key found. Run 'mmx auth' or set MINIMAX_API_KEY"}))
sys.exit(2)
