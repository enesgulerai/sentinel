import asyncio
import time

import aiohttp

API_URL = "http://localhost:8000/api/v1/transactions"
TOTAL_REQUESTS = 1000

# The exact same payload to test Redis blocking capabilities
PAYLOAD = {
    "Time": 406.0,
    "V1": -2.312226542,
    "V2": 1.951992011,
    "V3": -1.609850732,
    "V4": 3.997905588,
    "V5": -0.522187865,
    "V6": -1.426545319,
    "V7": -2.537387306,
    "V8": 1.391657248,
    "V9": -2.770089277,
    "V10": -2.772272145,
    "V11": 3.202033207,
    "V12": -2.899907388,
    "V13": -0.595221881,
    "V14": -4.289253782,
    "V15": 0.38972412,
    "V16": -1.14074718,
    "V17": -2.830055675,
    "V18": -0.016822468,
    "V19": 0.416955705,
    "V20": 0.126910559,
    "V21": 0.517232371,
    "V22": -0.035049369,
    "V23": -0.465211076,
    "V24": 0.320198199,
    "V25": 0.044519167,
    "V26": 0.177839798,
    "V27": 0.261145003,
    "V28": -0.143275875,
    "Amount": 1505.0,
}


async def send_request(session, req_id):
    start_time = time.perf_counter()
    try:
        async with session.post(API_URL, json=PAYLOAD) as response:
            resp_json = await response.json()
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {
                "status": response.status,
                "source": resp_json.get("source"),
                "time_ms": elapsed_ms,
            }
    except Exception:
        return {"status": 500, "source": "Error", "time_ms": 0}


async def run_load_test():
    print(
        f"Starting Load Test: Sending {TOTAL_REQUESTS} identical requests concurrently..."
    )
    print("-" * 60)

    start_total = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, i) for i in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)

    total_time_sec = time.perf_counter() - start_total

    redpanda_count = sum(1 for r in results if "Redpanda" in r["source"])
    redis_count = sum(1 for r in results if "Redis" in r["source"])
    avg_ms = sum(r["time_ms"] for r in results) / TOTAL_REQUESTS
    rps = TOTAL_REQUESTS / total_time_sec

    print("--- BENCHMARK RESULTS ---")
    print(f"Total Requests     : {TOTAL_REQUESTS}")
    print(f"Total Time         : {total_time_sec:.2f} seconds")
    print(f"Requests Per Second: {rps:.2f} RPS")
    print(f"Average Latency    : {avg_ms:.2f} ms per request")
    print("-" * 60)
    print(f"Routed to Redpanda (Processed) : {redpanda_count}")
    print(f"Blocked by Redis   (Duplicates): {redis_count}")
    print("-" * 60)
    print("Test completed.")


if __name__ == "__main__":
    asyncio.run(run_load_test())
