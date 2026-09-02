import requests
try:
    r = requests.post("http://localhost:5000/api/chat", json={"message": "hello"})
    print(r.status_code)
    print(r.text)
except Exception as e:
    print(e)
