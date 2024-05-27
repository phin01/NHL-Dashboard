# %%
import pandas as pd
import numpy as np

from tslearn.metrics import cdist_dtw
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform


def fill_series(series, max_length):
    padded = np.full(max_length, series.max())
    padded[:len(series)] = series
    return padded


# %%
game_results_src = "silver/game-results/game-results.csv"
game_results_destination = "gold/analytics-src/results-time-series.csv"


df = pd.read_csv(game_results_src)
df = df[['id', 'gameDate', 'season', 'homeTeamId', 'visitingTeamId', 'homePoints', 'awayPoints']]

# home/away data is in different columns, we should put them all under the same column and normalize names
df_home = df.rename(columns={"homeTeamId": "teamId", "homePoints": "points"}).drop(columns=["visitingTeamId", "awayPoints"])
df_away = df.rename(columns={"visitingTeamId": "teamId", "awayPoints": "points"}).drop(columns=["homeTeamId", "homePoints"])
df = pd.concat([df_home, df_away])
df['gameDate'] = pd.to_datetime(df['gameDate'])

df = df.sort_values(['season', 'teamId', 'gameDate'], ascending=[True, True, True]).reset_index(drop=True)

#%%
# running total for points as new column
df['runningPoints'] = df.groupby(['season', 'teamId'])['points'].cumsum()
df

#%%
"""
Now we create clusters with the time series using DTW, 
to try and group together teams that had similar points trends over the season
ie, strong start/weak finish, weak start/strong finish, etc
Analysis per season

Disclaimer:
Usually, all teams would have the same amount of games during a season
But during 2019/2020 season, it was interrupted due to COVID
So, for teams with fewer games, we consider their running total to 
remain the same for the games that were not played
"""

seasons = df.season.drop_duplicates().to_list()
performance_clusters = pd.DataFrame()

for season in seasons:

    # start with 2023-2024
    dtw = df[df['season'] == season]
    dtw = dtw[['teamId', 'runningPoints']]

    # store team IDs so we can match the clusters later
    team_ids = dtw.teamId.drop_duplicates()
   
    grouped_dtw = dtw.groupby('teamId')
    max_games = dtw.groupby('teamId').size().max()

    # use function to fill series up to the max amount of games
    # 2019 season was interrupted with uneven number of games between teams
    time_series = grouped_dtw['runningPoints'].apply(lambda p: fill_series(p.values, max_games)).to_list()
    time_series = np.array(time_series)

    distance_matrix = cdist_dtw(time_series)
    distance_matrix = squareform(distance_matrix)
    hierarchical_clustering = linkage(distance_matrix, method='ward')

    # create classifications for 3, 4 and 5 clusters
    # we'll see which makes better sense later
    defined_clusters = []
    for num_clusters in [3, 4, 5]:
        labels = fcluster(hierarchical_clustering, t=num_clusters, criterion='maxclust')
        defined_clusters.append(labels)

    team_clusters = pd.DataFrame(team_ids)
    team_clusters['3clusterGroup'] = defined_clusters[0]
    team_clusters['4clusterGroup'] = defined_clusters[1]
    team_clusters['5clusterGroup'] = defined_clusters[2]

    team_clusters['season'] = season

    performance_clusters = pd.concat([performance_clusters, team_clusters])

#%%
final_df = pd.merge(df, performance_clusters, how='left', left_on=['season', 'teamId'], right_on=['season', 'teamId'])
final_df.to_csv(game_results_destination, index=False)
