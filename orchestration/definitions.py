# ==================== #
#                      #
#       imports        #
#                      #
# ==================== #
# this file is used for running dagster locally
# this file is loaded directly as code location

from pathlib import Path
import os
import sys

import dlt
import dagster as dg
from dagster_dlt import DagsterDltResource, dlt_assets
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

# ==================== #
#                      #
#   paths & settings   #
# ==================== #

# repo root: .../big_data_cloud_group_11
REPO_ROOT = Path(__file__).resolve().parents[1]

# data_extract_load på import-sökvägen
sys.path.insert(0, str(REPO_ROOT / "data_extract_load"))
from load_job_ads import jobads_source  # noqa: E402

# DuckDB-fil: samma som i load_job_ads.py / profiles.yml
DEFAULT_DUCKDB_PATH = REPO_ROOT / "duck_pond" / "job_ads.duckdb"
DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(DEFAULT_DUCKDB_PATH))

# dbt-projekt-mapp
dbt_project_directory = REPO_ROOT / "data_transformation"

# profiles.yml ligger i data_transformation/
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", str(dbt_project_directory))

# ==================== #
#                      #
#       dlt Asset      #
#                      #
# ==================== #

dlt_resource = DagsterDltResource()


@dlt_assets(
    dlt_source=jobads_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="jobsearch",
        dataset_name="staging",
        destination=dlt.destinations.duckdb(credentials=DUCKDB_PATH),
    ),
)
def dlt_load(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    """Kör dlt-pipelinen och laddar in job ads till DuckDB."""
    context.log.info(f"Loading data into DuckDB at {DUCKDB_PATH}")
    yield from dlt.run(context=context)


# ==================== #
#                      #
#       dbt Asset      #
#                      #
# ==================== #
# this dbt asset needs dbt_packages pre-installed by 'dbt deps'

dbt_project = DbtProject(
    project_dir=dbt_project_directory,
    profiles_dir=DBT_PROFILES_DIR,
)

# References the dbt project object
dbt_resource = DbtCliResource(project_dir=dbt_project)

# Compiles the dbt project & allow Dagster to build an asset graph
dbt_project.prepare_if_dev()


# Yields Dagster events streamed from the dbt CLI
@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    """Kör dbt build och exponerar modeller som Dagster-assets."""
    yield from dbt.cli(["build"], context=context).stream()


# ==================== #
#                      #
#         Job          #
#                      #
# ==================== #

job_dlt = dg.define_asset_job(
    "job_dlt",
    selection=dg.AssetSelection.keys("dlt_jobads_source_jobsearch_resource"),
)

job_dbt = dg.define_asset_job(
    "job_dbt",
    selection=dg.AssetSelection.key_prefixes("warehouse", "marts"),
)


# ==================== #
#                      #
#       Schedule       #
#                      #
# ==================== #

schedule_dlt = dg.ScheduleDefinition(
    name="job_dlt_schedule",
    job=job_dlt,
    cron_schedule="00 08 * * *",
    execution_timezone="Europe/Stockholm",
)


# ==================== #
#                      #
#        Sensor        #
#                      #
# ==================== #

@dg.asset_sensor(asset_key=dg.AssetKey("dlt_jobads_source_jobsearch_resource"), job_name="job_dbt")
def dlt_load_sensor():
    """Triggar dbt-jobbet när dlt-asseten uppdateras."""
    yield dg.RunRequest()


# ==================== #
#                      #
#     Definitions      #
#                      #
# ==================== #

defs = dg.Definitions(
    assets=[dlt_load, dbt_models],
    resources={
        "dlt": dlt_resource,
        "dbt": dbt_resource,
    },
    jobs=[job_dlt, job_dbt],
    schedules=[schedule_dlt],
    sensors=[dlt_load_sensor],
)
