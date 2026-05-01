import json, sys

print(json.dumps({"error": "API_ERROR", "message": "Rate limit exceeded. Please try again later."}))
sys.exit(4)
