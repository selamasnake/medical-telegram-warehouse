from dagster import job, op, Nothing, In, ScheduleDefinition, Definitions
import subprocess

# Define Operations
@op
def scrape_telegram_data(context) -> Nothing:
    """Run the Telegram scraper"""
    context.log.info("Starting Telegram scraping...")
    subprocess.run(["python3", "src/scraper.py"], check=True)
    context.log.info("Telegram scraping completed")

@op(ins={"start": In(Nothing)})
def load_raw_to_postgres(context):
    """Load raw JSON to staging tables in PostgreSQL"""
    context.log.info("Loading raw JSON into PostgreSQL...")
    subprocess.run(["python3", "src/load_raw_telegram.py"], check=True)
    context.log.info("Load completed")

@op(ins={"start": In(Nothing)})
def run_dbt_transformations(context):
    """Run dbt models and tests"""
    context.log.info("Running dbt models...")
    subprocess.run(["dbt", "run", "--project-dir", "medical_warehouse"], check=True)
    context.log.info("dbt transformations completed")

@op(ins={"start": In(Nothing)})
def run_yolo_enrichment(context):
    """Run YOLO object detection on images"""
    context.log.info("Starting YOLO enrichment...")
    subprocess.run(["python3", "src/yolo_detect.py"], check=True)
    context.log.info("YOLO enrichment completed")


# Define Job (Pipeline)


@job
def full_pipeline():
    """Full ETL + dbt + YOLO enrichment workflow"""
    scrape_done = scrape_telegram_data()
    load_done = load_raw_to_postgres(start=scrape_done)
    dbt_done = run_dbt_transformations(start=load_done)
    run_yolo_enrichment(start=dbt_done)


# Schedule & Definitions


daily_schedule = ScheduleDefinition(
    job=full_pipeline,
    cron_schedule="0 6 * * *",
    execution_timezone="UTC"
)

defs = Definitions(
    jobs=[full_pipeline],
    schedules=[daily_schedule],
)