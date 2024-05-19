# Imports
import requests
import json
import os
import argparse
import sys

from azure.storage.blob import BlobServiceClient

import libs.credentials as c

LOCAL_FOLDER = os.path.join(os.path.dirname(__file__), "bronze", "team-ids")

# Function Definitions
def define_storage_mode(argparser):
    args = argparser.parse_args()

    if args.storage.lower() not in ["local", "azure"]:
        print("Invalid --storage (-s) option. Provide 'local' or 'azure'")
        sys.exit(1)

    if args.storage.lower() == "local":
        if not os.path.isdir(LOCAL_FOLDER):
            os.makedirs(LOCAL_FOLDER)
        return True
    else:
        return False

def ingest_team_ids(url):
    # Team IDs endpoint: https://api.nhle.com/stats/rest/en/team
    r = requests.get(url)
    data = r.json()
    if save_locally:
        filename = os.path.join(LOCAL_FOLDER, "team-ids.json")
        with open(filename, "w") as f:
            json.dump(data, f)
    else:
        blob_name = f"{AZURE_CONTAINER}team-ids.json"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(data=json.dumps(data), overwrite=True)

# Script gives you the option to save files locally or on Azure
# If an invalid option is provided, quit
parser = argparse.ArgumentParser()
parser.add_argument("--storage", "-s", default="local")
save_locally = define_storage_mode(parser)

if save_locally == False:
    # Configure Azure Blob Storage Credentials
    AZURE_CONTAINER = "raw/nhl/team-ids/"
    account_url = c.get_storage_account_url()
    default_credential = c.get_storage_account_credential()
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)
    container_name = "sports-bot"

# Game results come from a single endpoint, with results for all seasons since 1917
# Large file, but documentation doesn't seem to provide filtering options. Testing yielded no results
base_url = "https://api.nhle.com/stats/rest/en/team"

ingest_team_ids(base_url)
