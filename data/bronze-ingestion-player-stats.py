# %%
# Imports
import requests
import json
import os
import argparse
import sys
import re

from azure.storage.blob import BlobServiceClient

import libs.credentials as c

LOCAL_FOLDER = os.path.join(os.path.dirname(__file__), "bronze", "player-stats")

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

def ingest_player_stats(season_id, team_code):
    # Basic Player Stats: https://api-web.nhle.com/v1/club-stats/TOR/20222023/3
    # 2: Regular Season / 3: Playoffs
    game_types = [2, 3]
    for game_type in game_types:
        filename = f"{str(season_id)}_{team_code[0]}_{str(game_type)}.json"
        r = requests.get(f"{base_url}club-stats/{team_code[0]}/{season_id}/{game_type}")
        if r.status_code != 200:
            filename = f"{str(season_id)}_{team_code[1]}_{str(game_type)}.json"
            r = requests.get(f"{base_url}club-stats/{team_code[1]}/{season_id}/{game_type}")
        
        data = r.json()
        # if team didn't make the playoffs, skaters and goalies stats list will be empty. Skip saving these files
        if len(data['skaters']) > 0:
            if save_locally:
                filename = os.path.join(LOCAL_FOLDER, filename)
                with open(filename, "w") as f:
                    json.dump(data, f)
            else:
                blob_name = f"{AZURE_CONTAINER}{filename}.json"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(data=json.dumps(data), overwrite=True)


def get_teams_from_season(season_date):
    season_teams = []
    r = requests.get(f"{base_url}standings/{season_date}")
    data = r.json()['standings']
    for team in data:
        try:
            team_code_from_logo = re.search(r'/([^_/]+)_\d', team['teamLogo']).group(1)
        except:
            team_code_from_logo = "N/A"
        season_teams.append([team['teamAbbrev']['default'], team_code_from_logo])
    return season_teams

# Script gives you the option to save files locally or on Azure
# If an invalid option is provided, quit
parser = argparse.ArgumentParser()
parser.add_argument("--storage", "-s", default="local")
save_locally = define_storage_mode(parser)
# save_locally = True

if save_locally == False:
    # Configure Azure Blob Storage Credentials
    AZURE_CONTAINER = "raw/nhl/player-stats/"
    account_url = c.get_storage_account_url()
    default_credential = c.get_storage_account_credential()
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)
    container_name = "sports-bot"

# First step, get the end date for each season (it'll be used as a criteria to find the teams that played in each season)
base_url = "https://api-web.nhle.com/v1/"
all_seasons_endpoint =  "standings-season"
r = requests.get(f"{base_url}{all_seasons_endpoint}")
season_list = r.json()['seasons']

# Then get the teams for each season and query the player stats for each team/season combo
# For most teams, the Default Abbreviation works to query the players stats
# But in some cases that code won't work, but the code found in the logo's URL will
# So we pass a team array to the ingestion method, with the abbreviation at pos [0] and the logo code at pos [1]
# We'll call the API with the Abbreviation first, and if it doesn't return a 200 call, try with the logo code
for season in season_list:
    season_teams = get_teams_from_season(season['standingsEnd'])
    for team in season_teams:
        ingest_player_stats(season['id'], team)