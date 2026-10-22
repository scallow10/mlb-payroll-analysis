import pandas as pd
from pybaseball import standings

years = [2021, 2022, 2023, 2024, 2025]

all_seasons = []

for year in years:
    data = standings(year)

    season_data = pd.concat(data, ignore_index=True)

    season_data = season_data.drop(columns=["GB"])

    season_data = season_data.rename(columns={
        "Tm": "Team",
        "W": "Wins",
        "L": "Losses",
        "W-L%": "Win_Percentage"
    })

    season_data["Season"] = year

    all_seasons.append(season_data)

mlb_data = pd.concat(all_seasons, ignore_index=True)

print(mlb_data)
print("Number of rows:", len(mlb_data))
mlb_data.to_csv("data/cleaned/mlb_performance_2021_2025.csv", index=False)