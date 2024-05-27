# %%
import json
import os
import pandas as pd

# %%
standings_src = "bronze/standings/"
standings_destination = "silver/standings/standings.csv"

# focus on previous 10 seasons
season_files = os.listdir(standings_src)
season_files = season_files[-10:]

df = pd.DataFrame()

for filename in season_files:
    with open(os.path.join(standings_src,filename)) as f:
        standings_json = json.load(f)['standings']
        for team in standings_json:
            df_standings = pd.json_normalize(team)
            df = pd.concat([df, df_standings])

#%%
relevant_columns = [
    'clinchIndicator',
    'conferenceName',
    'divisionName',
    'goalFor',
    'goalAgainst',
    'homeGoalsFor',
    'homeGoalsAgainst',
    'homeLosses',
    'homeOtLosses',
    'homePoints',
    'homeRegulationPlusOtWins',
    'homeRegulationWins',
    'homeTies',
    'homeWins',
    'losses',
    'otLosses',
    'points',
    'regulationPlusOtWins',
    'regulationWins',
    'roadGoalsAgainst',
    'roadGoalsFor',
    'roadLosses',
    'roadOtLosses',
    'roadPoints',
    'roadRegulationPlusOtWins',
    'roadRegulationWins',
    'roadTies',
    'roadWins',
    'shootoutWins',
    'ties',
    'wins',
    'teamAbbrev.default',
    'seasonId'
]

df = df[relevant_columns]
df.to_csv(standings_destination, index=False)
