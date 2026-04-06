import requests

API_URL = "http://localhost:8000"


def test_health_check():
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_valid_transaction_ingestion():
    payload = {
        "Time": 0.0,
        "V1": 0.0,
        "V2": 0.0,
        "V3": 0.0,
        "V4": 0.0,
        "V5": 0.0,
        "V6": 0.0,
        "V7": 0.0,
        "V8": 0.0,
        "V9": 0.0,
        "V10": 0.0,
        "V11": 0.0,
        "V12": 0.0,
        "V13": 0.0,
        "V14": 0.0,
        "V15": 0.0,
        "V16": 0.0,
        "V17": 0.0,
        "V18": 0.0,
        "V19": 0.0,
        "V20": 0.0,
        "V21": 0.0,
        "V22": 0.0,
        "V23": 0.0,
        "V24": 0.0,
        "V25": 0.0,
        "V26": 0.0,
        "V27": 0.0,
        "V28": 0.0,
        "Amount": 100.0,
    }

    response = requests.post(f"{API_URL}/api/v1/transactions", json=payload)

    assert response.status_code == 202
    data = response.json()
    assert data["status"] in ["success", "ignored"]
    assert "source" in data


def test_invalid_transaction_payload():
    bad_payload = {"Time": 100.0, "V1": 1.5}

    response = requests.post(f"{API_URL}/api/v1/transactions", json=bad_payload)
    assert response.status_code == 422
