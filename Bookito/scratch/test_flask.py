import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web.app import app

client = app.test_client()

prompt = "Our organization needs a distributed workflow engine capable of executing business processes that may run for several weeks. The engine should survive crashes, retries, duplicate messages, version upgrades, and regional failures while guaranteeing exactly-once logical execution. The workflow language should support timers, parallel branches, compensation, retries, and human approval steps. Generate a feature design document comparing different workflow execution models."

response = client.post('/api/chat', json={"message": prompt})
print("Status:", response.status_code)
try:
    print("Response:", response.data.decode('utf-8'))
except Exception as e:
    print("Exception reading response:", e)
