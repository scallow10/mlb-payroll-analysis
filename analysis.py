import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import numpy as np
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

conn = sqlite3.connect("mlb_analysis.db")

query = """
SELECT
    p.Team,
    p.Team_ID,
    p.Season,
    p.Wins,
    p.Losses,
    s.Payroll,
    ROUND(s.Payroll * 1.0 / p.Wins, 2) AS Cost_Per_Win
FROM team_performance AS p
JOIN team_payroll AS s
    ON p.Team_ID = s.Team_ID
    AND p.Season = s.Season
ORDER BY Cost_Per_Win ASC
"""
results = pd.read_sql_query(query, conn)
print("\nFINAL DATA VALIDATION")

print("Total records:", len(results))

print("Missing values:")
print(results.isna().sum())

print("Duplicate team-seasons:",
      results.duplicated(subset=["Team_ID", "Season"]).sum())

print("Teams per season:")
print(results.groupby("Season")["Team_ID"].nunique())

conn.close()
print(results)
print("number of rows:", len(results))
print(results.head(10))
correlation = results["Payroll"].corr(results["Wins"])

print("Payroll vs Wins Correlation:", round(correlation, 3))

# Convert payroll to millions for easier reading
results["Payroll_Millions"] = results["Payroll"] / 1_000_000

# Create scatterplot
plt.figure(figsize=(10, 6))

plt.scatter(
    results["Payroll_Millions"],
    results["Wins"],
    alpha=0.6
)

plt.title("MLB Team Payroll vs. Wins (2021–2025)")
plt.xlabel("Team Payroll (Millions of Dollars)")
plt.ylabel("Regular Season Wins")

plt.grid(alpha=0.3)
plt.tight_layout()
# Calculate the line of best fit
slope, intercept = np.polyfit(
    results["Payroll_Millions"],
    results["Wins"],
    1
)

# Generate points for the regression line
x_values = np.linspace(
    results["Payroll_Millions"].min(),
    results["Payroll_Millions"].max(),
    100
)

y_values = slope * x_values + intercept

# Draw the regression line
plt.plot(
    x_values,
    y_values,
    color="red",
    linewidth=2,
    label="Regression Line"
)
# Calculate expected wins based on payroll
results["Expected_Wins"] = (
    slope * results["Payroll_Millions"] + intercept
)

# Calculate how much each team overperformed
results["Wins_Above_Expected"] = (
    results["Wins"] - results["Expected_Wins"]
)

# Sort teams by how much they exceeded expectations
top_overperformers = results.sort_values(
    by="Wins_Above_Expected",
    ascending=False
)

print("\nTop 10 Teams Above Expected Wins:")
print(
    top_overperformers[
        ["Team", "Season", "Wins", "Expected_Wins", "Wins_Above_Expected"]
    ].head(10).round(2)
)

plt.legend()

plt.savefig(
    "visuals/payroll_vs_wins.png",
    dpi=300,
    bbox_inches="tight"
)
# Find the 10 biggest underperformers
bottom_performers = results.sort_values(
    by="Wins_Above_Expected",
    ascending=True
)

print("\nBottom 10 Teams Compared to Expected Wins:")
print(
    bottom_performers[
        ["Team", "Season", "Wins", "Payroll_Millions",
         "Expected_Wins", "Wins_Above_Expected"]
    ].head(10).round(2)
)

plt.show()
# ==========================================
# GRAPH 2: FIVE-YEAR TEAM AVERAGES
# ==========================================

# Calculate average wins and payroll for each team
team_averages = results.groupby("Team_ID").agg(
    Average_Wins=("Wins", "mean"),
    Average_Payroll=("Payroll_Millions", "mean")
).reset_index()

print("\nFive-Year Team Averages:")
print(team_averages.round(2))
print("Number of teams:", len(team_averages))

# Create second scatterplot
plt.figure(figsize=(12, 8))

plt.scatter(
    team_averages["Average_Payroll"],
    team_averages["Average_Wins"],
    s=100
)

# Label each team with its abbreviation
for _, row in team_averages.iterrows():
    plt.annotate(
        row["Team_ID"],
        (row["Average_Payroll"], row["Average_Wins"]),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=9
    )

# Calculate regression line for five-year averages
avg_slope, avg_intercept = np.polyfit(
    team_averages["Average_Payroll"],
    team_averages["Average_Wins"],
    1
)

# Predict average wins based on average payroll
team_averages["Expected_Wins"] = (
    avg_slope * team_averages["Average_Payroll"] + avg_intercept
)

# Calculate wins above or below expected
team_averages["Wins_Above_Expected"] = (
    team_averages["Average_Wins"] - team_averages["Expected_Wins"]
)

x_line = np.linspace(
    team_averages["Average_Payroll"].min(),
    team_averages["Average_Payroll"].max(),
    100
)

y_line = avg_slope * x_line + avg_intercept

avg_correlation = team_averages["Average_Payroll"].corr(
    team_averages["Average_Wins"]
)

avg_r_squared = avg_correlation ** 2

plt.plot(
    x_line,
    y_line,
    color="red",
    linestyle="--",
    label=f"League Trend (R² = {avg_r_squared:.2f})"
)

plt.title("Average MLB Wins vs. Average Payroll (2021–2025)")
plt.xlabel("Average Annual Payroll ($ Millions)")
plt.ylabel("Average Wins Per Season")

plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "visuals/average_payroll_vs_wins.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
# Rank teams by five-year performance relative to payroll
team_rankings = team_averages.sort_values(
    by="Wins_Above_Expected",
    ascending=False
)

print("\nTOP 10 ORGANIZATIONS ABOVE EXPECTED WINS:")
print(
    team_rankings[
        ["Team_ID", "Average_Wins", "Average_Payroll",
         "Expected_Wins", "Wins_Above_Expected"]
    ].head(10).round(2).to_string(index=False)
)

print("\nBOTTOM 10 ORGANIZATIONS BELOW EXPECTED WINS:")
print(
    team_rankings[
        ["Team_ID", "Average_Wins", "Average_Payroll",
         "Expected_Wins", "Wins_Above_Expected"]
    ].tail(10).sort_values(
        by="Wins_Above_Expected"
    ).round(2).to_string(index=False)
)