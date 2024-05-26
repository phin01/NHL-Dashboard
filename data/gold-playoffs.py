#%%
import pandas as pd
import numpy as np


#%%

# %%
playoffs_src = "silver/playoffs/playoffs.csv"
standings_src = "silver/standings/standings.csv"
playoffs_destination = "gold/playoffs.csv"
# %%

"""
We'll create a simple factor to determine how 'obvious' the series result was
If bottom team wins, give the series a +1 rating
If top team wins, give the series a -1 rating
Rating will be multiplied by the points difference between both teams in the regular season, in %

Example series:
    Top seed: 100 points
    Bottom seed: 90 points
    Series result: Top seed wins
    Series Factor: (-1) * (100/90) = -1.11
"""

df_standings = pd.read_csv(standings_src)
df_standings = df_standings[["seasonId", "points", "teamAbbrev.default"]]

#%%

df = pd.read_csv(playoffs_src)

df = pd.merge(df, df_standings, how="left", left_on=["seasonId", "bottomSeedTeam"], right_on=["seasonId", "teamAbbrev.default"])
df = df.rename(columns={"points": "bottomSeedPoints"})

df = pd.merge(df, df_standings, how="left", left_on=["seasonId", "topSeedTeam"], right_on=["seasonId", "teamAbbrev.default"])
df = df.rename(columns={"points": "topSeedPoints"})

df = df.drop(columns=["teamAbbrev.default_x", "teamAbbrev.default_y"])
# %%

df["pointsFactor"] = df["topSeedPoints"] / df["bottomSeedPoints"]
df["resultFactor"] = np.where(df["winningTeamId"] == df["topSeedId"], -1, 1)
df["seriesFactor"] = df["pointsFactor"] * df["resultFactor"]

df.to_csv(playoffs_destination, index=False)
# %%
