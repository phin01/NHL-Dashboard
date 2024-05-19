# Imports
import requests
import json
import os
import argparse
import sys

from azure.storage.blob import BlobServiceClient

import libs.credentials as c

LOCAL_FOLDER = os.path.join(os.path.dirname(__file__), "bronze", "standings")

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

def ingest_season_standings(season_id, season_date):
    # Individual season endpoint: https://api-web.nhle.com/v1/standings/2024-04-18
    r = requests.get(f"{base_url}standings/{season_date}")
    data = r.json()
    if save_locally:
        filename = os.path.join(LOCAL_FOLDER, f"{str(season_id)}.json")
        with open(filename, "w") as f:
            json.dump(data, f)
    else:
        blob_name = f"{AZURE_CONTAINER}{str(season_id)}.json"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(data=json.dumps(data), overwrite=True)

# Script gives you the option to save files locally or on Azure
# If an invalid option is provided, quit
parser = argparse.ArgumentParser()
parser.add_argument("--storage", "-s", default="local")
save_locally = define_storage_mode(parser)

if save_locally == False:
    # Configure Azure Blob Storage Credentials
    AZURE_CONTAINER = "raw/nhl/standings/"
    account_url = c.get_storage_account_url()
    default_credential = c.get_storage_account_credential()
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)
    container_name = "sports-bot"

# First step, get the end date for each season (it'll be used as a criteria to call standings for each season)
base_url = "https://api-web.nhle.com/v1/"
all_seasons_endpoint =  "standings-season"
r = requests.get(f"{base_url}{all_seasons_endpoint}")
season_list = r.json()['seasons']

# Then get full season standings and save them as {season_id}.json
# Either locally or in blob storage
for season in season_list:
    ingest_season_standings(season['id'], season['standingsEnd'])
