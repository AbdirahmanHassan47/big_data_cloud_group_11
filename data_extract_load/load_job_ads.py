import dlt
import requests
import json
from pathlib import Path

# Gör så att staging-tratten töms vid varje körning
dlt.config["load.truncate_staging_dataset"] = True


def _get_ads(url_for_search, params):
    headers = {"accept": "application/json"}
    response = requests.get(url_for_search, headers=headers, params=params)
    response.raise_for_status()
    return json.loads(response.content.decode("utf8"))


@dlt.resource(table_name="job_ads", write_disposition="replace")
def jobsearch_resource(occupation_fields=None, base_query="", limit=100):
    url = "https://jobsearch.api.jobtechdev.se"
    url_for_search = f"{url}/search"

    if not occupation_fields:
        occupation_fields = ("MVqp_eS8_kDZ", "E7hm_BLq_fqZ", "ASGV_zcE_bWf")

    if isinstance(occupation_fields, str):
        fields_iter = [occupation_fields]
    else:
        fields_iter = list(occupation_fields)

    for occupation_field in fields_iter:
        offset = 0
        while True:
            page_params = {
                "q": base_query,
                "limit": limit,
                "occupation-field": occupation_field,
                "offset": offset,
            }
            data = _get_ads(url_for_search, page_params)
            hits = data.get("hits", [])
            if not hits:
                break

            for ad in hits:
                ad["_occupation_field"] = occupation_field
                yield ad

            if len(hits) < limit or offset > 1900:
                break
            offset += limit


@dlt.source
def jobads_source():
    return jobsearch_resource(
        occupation_fields=("MVqp_eS8_kDZ", "E7hm_BLq_fqZ", "ASGV_zcE_bWf"),
        base_query="",
        limit=100,
    )


# 🔽🔽🔽 HÄR BÖRJAR DEN VIKTIGA DELEN 🔽🔽🔽

# DuckDB-filen där vi vill skriva (samma som dbt använder: ../duck_pond/job_ads.duckdb)
DUCKDB_PATH = Path(__file__).parents[1] / "duck_pond" / "job_ads.duckdb"


def main():
    print("🚀 Startar DLT-pipeline...")
    print(f"➡ DuckDB-fil: {DUCKDB_PATH}")

    pipeline = dlt.pipeline(
        pipeline_name="job_ads_pipeline",
        destination=dlt.destinations.duckdb(credentials=str(DUCKDB_PATH)),
        dataset_name="staging",
    )

    print("📡 Hämtar annonser från jobtech-API...")
    load_info = pipeline.run(
        jobads_source(),
        table_name="job_ads",  # hamnar som staging.job_ads
    )

    print("✅ Load completed.")
    print(load_info)


if __name__ == "__main__":
    main()
