# %%
import json
import pandas as pd
import numpy as np

# %%
game_results_src = "bronze/game-results/game-results.json"
game_resuts_destination = "silver/game-results/game-results.csv"


with open(game_results_src) as f:
    game_results_json = json.load(f)

df = pd.DataFrame(game_results_json['data'])

# Keep only regular season games
df = df[df.gameType == 2]

#%%
# Focus on the previous 10 seasons
relevant_seasons = (
    df['season']
    .sort_values(ascending=False)
    .drop_duplicates()
    .head(10)
    .values.tolist()
)

seasons = df[df.season.isin(relevant_seasons)]

#%%

# Define game winner, either Home or Away team
seasons['winner'] = np.where(seasons['homeScore'] > seasons['visitingScore'], "H", "A")

home_result = [
    seasons['homeScore'] > seasons['visitingScore'],
    seasons['period'] > 3,
    seasons['period'] == 3,
    ]

away_result = [
    seasons['homeScore'] < seasons['visitingScore'],
    seasons['period'] > 3,
    seasons['period'] == 3,
    ]

possible_points = [2, 1, 0]

# Calculate home and away points based on game results
# (OT/SO losses are worth one point, regulation losses worth 0 points)
seasons['homePoints'] = np.select(home_result, possible_points)
seasons['awayPoints'] = np.select(away_result, possible_points)
#%%
seasons.head()
#%%

seasons = seasons[
    ['id',
     'gameDate',
      'homeScore',
      'homeTeamId',
      'period',
      'season',
      'visitingScore',
      'visitingTeamId',
      'winner',
      'homePoints',
      'awayPoints']
]

seasons['period'] = seasons['period'].astype(int)

seasons.to_csv(game_resuts_destination, index=False)
