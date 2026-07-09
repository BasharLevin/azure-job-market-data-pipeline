from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import os


REQUIRED_ENV_VARS = {
    "AZURE_SQL_SERVER": "your_server_name.database.windows.net",
    "AZURE_SQL_DATABASE": "your_database_name",
    "AZURE_SQL_USERNAME": "your_username",
    "AZURE_SQL_PASSWORD": "your_password",
    "AZURE_SQL_DRIVER": "",
}

CSV_TABLES = {
    "job_ads.csv": "job_ads",
    "skills.csv": "skills",
    "job_ad_skills.csv": "job_ad_skills",
}

PROCESSED_FOLDER = Path("data/processed")


def get_required_env_value(name, placeholder):
    value = os.getenv(name)

    if value is None or value.strip() == "":
        print(f"Missing required environment variable: {name}")
        return None

    if placeholder and value.strip() == placeholder:
        print(f"Please replace the placeholder value for {name} in your .env file.")
        return None

    return value


def load_sql_settings():
    settings = {}

    for name, placeholder in REQUIRED_ENV_VARS.items():
        value = get_required_env_value(name, placeholder)
        if value is None:
            return None
        settings[name] = value

    return settings


def check_csv_files():
    if not PROCESSED_FOLDER.exists():
        print(f"Missing processed data folder: {PROCESSED_FOLDER}")
        print("Run the transformation step first so the CSV files are created.")
        return None

    csv_paths = {}

    for csv_name, table_name in CSV_TABLES.items():
        csv_path = PROCESSED_FOLDER / csv_name

        if not csv_path.exists():
            print(f"Missing CSV file: {csv_path}")
            print("Run the transformation step first, then try loading to SQL again.")
            return None

        csv_paths[table_name] = csv_path

    return csv_paths


def create_sql_engine(settings):
    connection_url = URL.create(
        "mssql+pyodbc",
        username=settings["AZURE_SQL_USERNAME"],
        password=settings["AZURE_SQL_PASSWORD"],
        host=settings["AZURE_SQL_SERVER"],
        port=1433,
        database=settings["AZURE_SQL_DATABASE"],
        query={
            "driver": settings["AZURE_SQL_DRIVER"],
            "Encrypt": "yes",
            "TrustServerCertificate": "no",
            "Connection Timeout": "60",
        },
    )

    return create_engine(connection_url)


def main():
    load_dotenv()

    settings = load_sql_settings()
    if settings is None:
        print("SQL load stopped. Please update your .env file and try again.")
        return

    csv_paths = check_csv_files()
    if csv_paths is None:
        print("SQL load stopped because one or more CSV files are missing.")
        return

    try:
        print(f"Connecting to Azure SQL server: {settings['AZURE_SQL_SERVER']}")
        print(f"Database: {settings['AZURE_SQL_DATABASE']}")

        engine = create_sql_engine(settings)

        for table_name, csv_path in csv_paths.items():
            print(f"Loading table: {table_name}")

            dataframe = pd.read_csv(csv_path)

            dataframe.to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",
                index=False,
            )

            print(f"Loaded {csv_path} into Azure SQL table: {table_name}")

        print("All CSV files loaded into Azure SQL successfully.")

    except Exception as error:
        print("SQL load failed.")
        print("Check your .env SQL settings, network access, firewall rules, and ODBC driver.")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
