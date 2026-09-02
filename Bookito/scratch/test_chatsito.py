import requests
import json

payload = {
    "Model": "",
    "Messages": [
        {"Role": "System", "Content": "System prompt"},
        {"Role": "User", "Content": "Prompt: Our organization needs a distributed workflow engine...\n\nContext:\nNo context"}
    ],
    "Tools": []
}

try:
    resp = requests.post("http://localhost:5257/api/chat/stream", json=payload, stream=True)
    print("Status:", resp.status_code)
    for line in resp.iter_lines():
        if line:
            print(line.decode('utf-8'))
except Exception as e:
    print("Error:", e)
