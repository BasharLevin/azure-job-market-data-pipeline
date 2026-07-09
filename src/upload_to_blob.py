from pathlib import Path

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os


CONNECTION_STRING_PLACEHOLDER = "paste_your_connection_string_here"


def get_required_env_value(name):
    value = os.getenv(name)

    if value is None or value.strip() == "":
        print(f"Missing required environment variable: {name}")
        return None

    if value == CONNECTION_STRING_PLACEHOLDER:
        print(f"Please replace the placeholder value for {name} in your .env file.")
        return None

    return value


def find_processed_folder():
    possible_folders = [
        Path("data/processed"),
        Path("src/data/processed"),
    ]

    for folder in possible_folders:
        if folder.exists() and folder.is_dir():
            return folder

    print("Could not find a processed data folder.")
    print("Checked these locations:")
    for folder in possible_folders:
        print(f"- {folder}")

    return None


def main():
    load_dotenv()

    connection_string = get_required_env_value("AZURE_STORAGE_CONNECTION_STRING")
    container_name = get_required_env_value("AZURE_CONTAINER_NAME")

    if connection_string is None or container_name is None:
        print("Upload stopped. Please update your .env file and try again.")
        return

    processed_folder = find_processed_folder()
    if processed_folder is None:
        print("Upload stopped because no processed CSV folder was found.")
        return

    csv_files = sorted(processed_folder.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {processed_folder}.")
        print("Upload stopped because there is nothing to upload.")
        return

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        for csv_file in csv_files:
            blob_name = f"processed/{csv_file.name}"

            with csv_file.open("rb") as file_data:
                container_client.upload_blob(
                    name=blob_name,
                    data=file_data,
                    overwrite=True,
                )

            print(f"Uploaded {csv_file} to Azure Blob Storage as {blob_name}")

        print("All CSV files uploaded successfully.")

    except Exception as error:
        print("Upload failed.")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
