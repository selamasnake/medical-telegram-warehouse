# pipeline.py
from dagster import job, op, failure_hook, ScheduleDefinition
import subprocess


# Failure hook

@failure_hook
def on_failure(context):
    """Log job failure"""
    context.log.error(f"Job failed: {context.job_name}")
    # Optional: add Slack/email notifications here


# Define individual operations

@op
def scrape_telegram_data(context):
    """Run the Telegram scraper"""
    context.log.info("Starting Telegram scraping...")
    result = subprocess.run(
        ["python3", "src/scraper.py"],
        check=True,
        capture_output=True,
        text=True
    )
    context.log.info(result.stdout)
    context.log.info("Telegram scraping completed")

@op
def load_raw_to_postgres(context):
    """Load raw JSON to staging tables in PostgreSQL"""
    context.log.info("Loading raw JSON into PostgreSQL...")
    result = subprocess.run(
        ["python3", "src/load_raw_telegram.py"],
        check=True,
        capture_output=True,
        text=True
    )
    context.log.info(result.stdout)
    context.log.info("Load completed")

@op
def run_dbt_transformations(context):
    """Run dbt models and tests"""
    context.log.info("Running dbt models...")
    run_result = subprocess.run(
        ["dbt", "run", "--project-dir", "medical_warehouse"],
        check=True,
        capture_output=True,
        text=True
    )
    context.log.info(run_result.stdout)

    context.log.info("Running dbt tests...")
    test_result = subprocess.run(
        ["dbt", "test", "--project-dir", "medical_warehouse"],
        check=True,
        capture_output=True,
        text=True
    )
    context.log.info(test_result.stdout)
    context.log.info("dbt transformations and tests completed")

@op
def run_yolo_enrichment(context):
    """Run YOLO object detection on images"""
    context.log.info("Starting YOLO enrichment...")
    result = subprocess.run(
        ["python3", "src/yolo_detect.py"],
        check=True,
        capture_output=True,
        text=True
    )
    context.log.info(result.stdout)
    context.log.info("YOLO enrichment completed")


# Define the pipeline

# @job(
#     failure_hooks={on_failure}
# )
def full_pipeline():
    """Full ETL + dbt + YOLO enrichment workflow"""
    scrape = scrape_telegram_data()
    load = load_raw_to_postgres()
    dbt = run_dbt_transformations()
    yolo = run_yolo_enrichment()

    # Sequential execution
    scrape >> load >> dbt >> yolo


# Schedule (daily at 6 AM UTC)

daily_schedule = ScheduleDefinition(
    job=full_pipeline,
    cron_schedule="0 6 * * *",
    execution_timezone="UTC"
)
