import pandas as pd

# Years we want to analyze
years = [2021, 2022, 2023, 2024, 2025]

# Empty list to store each cleaned season
all_payroll = []

# Go through each season
for year in years:

    # Read the raw payroll CSV for that year
    payroll = pd.read_csv(f"data/raw/payroll_{year}.csv")

    # Keep only the columns we need
    payroll = payroll[["Team", "Total PayrollAllocations"]]

    # Remove blank rows
    payroll = payroll.dropna(subset=["Team"])

    # Remove the Spotrac averages row
    payroll = payroll[payroll["Team"] != "Averages"]

    # Reset row numbers
    payroll = payroll.reset_index(drop=True)

    # Remove $ and commas, then convert payroll to integers
    payroll["Total PayrollAllocations"] = (
        payroll["Total PayrollAllocations"]
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(int)
    )

    # Rename payroll column
    payroll = payroll.rename(columns={
        "Total PayrollAllocations": "Payroll"
    })

    # Add the season
    payroll["Season"] = year

    # Save each individual cleaned season
    payroll.to_csv(
        f"data/cleaned/payroll_{year}_cleaned.csv",
        index=False
    )

    # Add this season to our list
    all_payroll.append(payroll)


# Combine all five seasons into one DataFrame
payroll_data = pd.concat(all_payroll, ignore_index=True)

# Save the combined dataset
payroll_data.to_csv(
    "data/cleaned/mlb_payroll_2021_2025.csv",
    index=False
)

# Check the final result
print(payroll_data)
print("Number of rows:", len(payroll_data))