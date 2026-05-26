import json

import requests


def test_sentinel_api():
    url = "http://localhost:8000/api/v1/transactions"
    headers = {"Content-Type": "application/json"}

    print("Reading payload.json...")
    try:
        with open("payload.json") as file:
            payload = json.load(file)

        print(f"Sending POST request to {url}...")
        response = requests.post(url, json=payload, headers=headers)

        print("-" * 40)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        print("-" * 40)

    except FileNotFoundError:
        print("Error: payload.json not found in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    test_sentinel_api()
