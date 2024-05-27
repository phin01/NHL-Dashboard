# %%
import json
import pandas as pd
import numpy as np

# %%
team_ids_src = "bronze/team-ids/team-ids.json"
team_ids_destination = "silver/team-ids/team-ids.csv"


with open(team_ids_src) as f:
    team_ids_json = json.load(f)

df = pd.DataFrame(team_ids_json['data'])
teams = df[['id','fullName','triCode']]
teams.to_csv(team_ids_destination, index=False)