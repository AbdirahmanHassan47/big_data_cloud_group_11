from pathlib import Path
import duckdb

# Pekar på DuckDB-filen i projektroten: duck_pond/job_ads.duckdb
FILES_SHARE_PATH = (
    Path(__file__).resolve().parents[1] / "duck_pond" / "job_ads.duckdb"
)

def query_job_listings(query: str):
    """
    Kör en SELECT-fråga mot DuckDB och returnerar resultatet som en pandas DataFrame.
    """
    with duckdb.connect(FILES_SHARE_PATH, read_only=True) as conn:
        conn.execute("SET schema 'marts'")
        return conn.execute(query).df()
