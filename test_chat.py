import requests
import sys

try:
    response = requests.post(
        "http://localhost:8000/chat",
        json={"session_id": "test-session", "query": "hello"}
    )
    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Failed:", response.status_code, response.text)
        sys.exit(1)
except Exception as e:
    print("Error:", e)
    sys.exit(1)
