# %%
import json
import os
import pandas as pd

# %%
playoffs_src = "bronze/playoffs/"
playoffs_destination = "silver/playoffs/playoffs.csv"

# focus on previous 10 seasons
season_files = os.listdir(playoffs_src)
season_files = season_files[-10:]

def extract_playoff_data(filename):
    playoff_data = []
    with open(os.path.join(playoffs_src,filename)) as f:
        playoffs_json = json.load(f)
        for round in playoffs_json['rounds']:
            for serie in round['series']:
                serie['seasonId'] = playoffs_json['seasonId']
                serie['bottomSeedTeam'] = serie['bottomSeed']['abbrev']
                serie['bottomSeedId'] = serie['bottomSeed']['id']
                serie['bottomSeedWins'] = serie['bottomSeed']['wins']
                serie['topSeedTeam'] = serie['topSeed']['abbrev']
                serie['topSeedId'] = serie['topSeed']['id']
                serie['topSeedWins'] = serie['topSeed']['wins']
                serie.pop('bottomSeed')
                serie.pop('topSeed')
                serie.pop('seriesLink')
                playoff_data.append(serie)
    return playoff_data


all_playoffs = []
for filename in season_files:
    all_playoffs.append(extract_playoff_data(filename))

# flatten the list of lists
all_playoffs = [item for sublist in all_playoffs for item in sublist]


df = pd.DataFrame(all_playoffs)
df.to_csv(playoffs_destination, index=False)
