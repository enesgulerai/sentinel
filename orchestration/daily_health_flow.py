from datetime import datetime

from prefect import flow, task


# DYNAMIC NAME GENERATOR
def generate_run_name():
    return datetime.now().strftime("%d-%m-%y_Health-Check_%H-%M")


# TASK 1: Check API and System Health
@task(retries=2, retry_delay_seconds=5)
def check_api_health():
    print("[WORKER 1] Checking Sentinel API health status...")
    api_status = {"status": "online", "model_version": "0.4.0", "uptime": "99.9%"}
    print(f"[WORKER 1] System is operational. Version: {api_status['model_version']}")
    return api_status


# TASK 2: Generate Report and Alert
@task
def generate_daily_report(health_data):
    print("[WORKER 2] Processing health data for daily report...")
    if health_data["status"] != "online":
        raise ValueError("CRITICAL ERROR: API is DOWN! Triggering incident...")

    report = f"DAILY REPORT: All systems functioning normally. Uptime: {health_data['uptime']}"
    print("[WORKER 2] Report generated successfully.")
    return report


# MAIN FLOW
@flow(name="Sentinel-Daily-Health-Check", flow_run_name=generate_run_name)
def daily_health_check_pipeline():
    print("--- ORCHESTRATOR PIPELINE STARTED ---")

    health_data = check_api_health()
    final_report = generate_daily_report(health_data)

    print("--- ORCHESTRATOR PIPELINE COMPLETED ---")
    return final_report


if __name__ == "__main__":
    daily_health_check_pipeline()
