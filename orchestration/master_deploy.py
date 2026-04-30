from daily_health_flow import daily_health_check_pipeline
from data_ingestion_flow import data_ingestion_pipeline
from model_training_flow import model_training_flow
from prefect import serve

if __name__ == "__main__":
    print("🚀 Starting Sentinel Master Orchestrator...")

    health_deploy = daily_health_check_pipeline.to_deployment(
        name="daily-health-monitor", cron="0 9 * * *", tags=["health", "docker"]
    )

    ingest_deploy = data_ingestion_pipeline.to_deployment(
        name="hourly-data-ingestion", cron="0 * * * *", tags=["etl", "docker"]
    )

    train_deploy = model_training_flow.to_deployment(
        name="weekly-model-training", parameters={"save_model": True}, cron="0 0 * * 0", tags=["mlops", "training"]
    )

    serve(health_deploy, ingest_deploy, train_deploy)
