"""Script to sync data from MotherDuck to local DuckDB."""

import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv

# Load .env from backend directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def sync_from_motherduck(
    motherduck_db: str,
    motherduck_token: str,
    local_db_path: str,
    source_schema: str = "dmt",
) -> None:
    """
    Sync tables from MotherDuck to local DuckDB.

    Args:
        motherduck_db: Name of the MotherDuck database
        motherduck_token: MotherDuck authentication token
        local_db_path: Path to local DuckDB file
        source_schema: Schema to copy from MotherDuck (default: dmt)
    """
    # Ensure local database directory exists
    Path(local_db_path).parent.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to MotherDuck database: {motherduck_db}")

    with duckdb.connect(f"md:{motherduck_db}?motherduck_token={motherduck_token}") as conn:
        # List tables from MotherDuck BEFORE attaching local database
        print(f"Checking for tables in {motherduck_db}.{source_schema}...")
        tables = conn.execute(f"SHOW TABLES FROM {source_schema}").fetchall()

        if not tables:
            print(f"No tables found in schema '{source_schema}'")
            return

        print(f"Found {len(tables)} tables to sync:")
        for (table_name,) in tables:
            print(f"  - {table_name}")

        # Now attach local database
        conn.execute(f"ATTACH '{local_db_path}' AS local_db")

        # Create schema in local database if needed
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS local_db.{source_schema}")

        # Copy each table
        for (table_name,) in tables:
            print(f"Copying {table_name}...")
            conn.execute(f"""
                CREATE OR REPLACE TABLE local_db.{source_schema}.{table_name} AS
                SELECT * FROM {source_schema}.{table_name}
            """)

        # Force checkpoint to persist data
        conn.execute("FORCE CHECKPOINT")

    print("Sync complete!")


def main() -> None:
    """Run sync script with environment variables."""
    motherduck_db = os.getenv("MOTHERDUCK_DB")
    motherduck_token = os.getenv("MOTHERDUCK_TOKEN")
    local_db_path = os.getenv("DUCKDB_PATH", "../data/local_dmt.duckdb")
    source_schema = os.getenv("MOTHERDUCK_SCHEMA", "dmt")

    if not motherduck_db or not motherduck_token:
        raise ValueError("MOTHERDUCK_DB and MOTHERDUCK_TOKEN environment variables required")

    sync_from_motherduck(
        motherduck_db=motherduck_db,
        motherduck_token=motherduck_token,
        local_db_path=local_db_path,
        source_schema=source_schema,
    )


if __name__ == "__main__":
    main()
