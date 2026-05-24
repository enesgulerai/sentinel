import random
import time
import uuid

import requests

URL = "http://localhost:8000/api/v1/transactions"

print("Sentinel AI - Traffic Generator Started...")
while True:
    payload = {
        "transaction_id": f"TX-{uuid.uuid4().hex[:8].upper()}",
        "Amount": round(random.uniform(10.0, 5000.0), 2),
        "user_id": f"usr_{random.randint(1, 999)}",
    }

    try:
        requests.post(URL, json=payload)
        time.sleep(random.uniform(0.05, 0.15))
    except Exception:
        pass
