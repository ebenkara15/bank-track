from dagster import (
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_modules,
)
from . import worker

all_assets = load_assets_from_modules([worker])

fetch_transactions_job = define_asset_job(
    "fetch_transactions_job", selection=AssetSelection.all()
)

fetch_transactions_schedule = ScheduleDefinition(
    name="fetch_transactions_schedule",
    cron_schedule="* * * * *",
    job=fetch_transactions_job,
)

defs = Definitions(
    assets=all_assets,
    schedules=[fetch_transactions_schedule],
)
