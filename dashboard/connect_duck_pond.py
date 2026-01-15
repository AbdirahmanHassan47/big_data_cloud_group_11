import os
from pathlib import Path
import duckdb
import pandas as pd

FILES_SHARE_PATH = (
    os.getenv("FILES_SHARE_PATH")
    or os.getenv("DUCKDB_PATH")
    or str(Path(__file__).resolve().parents[1] / "duck_pond" / "job_ads.duckdb")
)

def query_job_listings(query: str) -> pd.DataFrame:
    if not os.path.exists(FILES_SHARE_PATH):
        return pd.DataFrame()

    try:
        with duckdb.connect(FILES_SHARE_PATH, read_only=True) as conn:
            conn.execute("SET schema 'marts'")
            return conn.execute(query).df()
    except duckdb.IOException:
        return pd.DataFrame()
