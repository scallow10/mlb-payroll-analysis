import pandas as pd
import sqlite3

performance = pd.read_csv(
    "data/cleaned/mlb_performance_2021_2025.csv"
)
print(performance["Team"].unique())

team_mapping = {
    "Arizona Diamondbacks": "ARI",
    "Atlanta Braves": "ATL",
    "Baltimore Orioles": "BAL",
    "Boston Red Sox": "BOS",
    "Chicago Cubs": "CHC",
    "Chicago White Sox": "CHW",
    "Cincinnati Reds": "CIN",
    "Cleveland Indians": "CLE",
    "Cleveland Guardians": "CLE",
    "Colorado Rockies": "COL",
    "Detroit Tigers": "DET",
    "Houston Astros": "HOU",
    "Kansas City Royals": "KC",
    "Los Angeles Angels": "LAA",
    "Los Angeles Dodgers": "LAD",
    "Miami Marlins": "MIA",
    "Milwaukee Brewers": "MIL",
    "Minnesota Twins": "MIN",
    "New York Mets": "NYM",
    "New York Yankees": "NYY",
    "Oakland Athletics": "ATH",
    "Athletics": "ATH",
    "Philadelphia Phillies": "PHI",
    "Pittsburgh Pirates": "PIT",
    "San Diego Padres": "SD",
    "San Francisco Giants": "SF",
    "Seattle Mariners": "SEA",
    "St. Louis Cardinals": "STL",
    "Tampa Bay Rays": "TB",
    "Texas Rangers": "TEX",
    "Toronto Blue Jays": "TOR",
    "Washington Nationals": "WSH"
}
performance["Team_ID"] = performance["Team"].map(team_mapping)

print(performance[["Team", "Team_ID", "Season"]].head(10))

print("Missing team IDs:", performance["Team_ID"].isna().sum())
payroll = pd.read_csv(
    "data/cleaned/mlb_payroll_2021_2025.csv"
)

payroll["Team_ID"] = payroll["Team"].replace({
    "OAK": "ATH"
})

print(payroll.head())
print("Number of payroll rows:", len(payroll))

matched = performance.merge(
    payroll,
    on=["Team_ID", "Season"],
    how="inner"
)

print("Matched rows:", len(matched))
print(matched.head())

conn = sqlite3.connect("mlb_analysis.db")

print("Database connected successfully!")
performance.to_sql(
    "team_performance",
    conn,
    if_exists="replace",
    index=False
)

payroll.to_sql(
    "team_payroll",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()
conn.close()

print("SQL tables created successfully!")