import os
import gdown
from tqdm import tqdm
import os
import pandas as pd
from datetime import datetime
import glob


def combine_csv_files(start_year=2014, end_year=2025):
    """
    Combine CSV files from a specified date range into a single DataFrame.

    Args:
        start_year (int): Starting year for data (inclusive)
        end_year (int): Ending year for data (inclusive)

    Returns:
        pd.DataFrame: Combined DataFrame with data from the specified range
    """
    # Directory containing CSV files
    csv_dir = "database/csv_files"

    # Get all CSV files
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {csv_dir}")

    # Initialize an empty list to store DataFrames
    dfs = []

    # Read and combine files
    for file in csv_files:
        # Extract year from filename
        try:
            year = int(os.path.basename(file).split("_")[0])
        except (ValueError, IndexError):
            print(f"Could not extract year from filename: {file}")
            continue

        # Check if year is within the specified range
        if start_year <= year <= end_year:
            print(f"Processing data for year {year}...")
            try:
                df = pd.read_csv(file)
                # Add year column if it doesn't exist
                if "year" not in df.columns:
                    df["year"] = year
                dfs.append(df)
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")

    if not dfs:
        raise ValueError(
            f"No data found for the specified range {start_year}-{end_year}"
        )

    # Combine all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)

    # Sort by date if a date column exists
    date_columns = ["date", "game_date", "match_date"]
    for col in date_columns:
        if col in combined_df.columns:
            combined_df[col] = pd.to_datetime(combined_df[col])
            combined_df = combined_df.sort_values(col)
            break

    return combined_df


def save_combined_data(df, output_file="database/combined_data.csv"):
    """
    Save the combined DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to save
        output_file (str): Path to save the output file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")


def download_csv_files():
    # Create a directory to store the CSV files if it doesn't exist
    output_dir = "database/csv_files"
    os.makedirs(output_dir, exist_ok=True)

    # Google Drive folder URL
    folder_url = (
        "https://drive.google.com/drive/u/1/folders/1gLSw0RLjBbtaNy0dgnGQDAZOHIgCe-HH"
    )

    # Get the list of files in the folder
    file_ids = gdown.download_folder(folder_url, output=output_dir, quiet=False)

    # Filter files to keep only 2024 and 2025 data
    filtered_files = [f for f in file_ids if any(year in f for year in ["2024", "2025"])]

    print(f"Downloaded {len(filtered_files)} files to {output_dir} (2024-2025 data only)")

def combine_dfs(start_year, end_year):
    try:
        # You can modify these years as needed
        #        start_year = 2023
        #       end_year = 2025

        print(f"Combining data from {start_year} to {end_year}...")
        combined_df = combine_csv_files(start_year, end_year)

        print(f"\nTotal rows in combined dataset: {len(combined_df)}")
        print("\nColumns in the dataset:")
        print(combined_df.columns.tolist())

        # Save the combined data
        save_combined_data(combined_df)

    except Exception as e:
        print(f"Error: {str(e)}")


def treat_data():
    df = pd.read_csv("database/combined_data.csv")

    df = df.query("datacompleteness == 'complete'").drop(columns=["datacompleteness"])
    # Create a new identification for gameid to make it smaller
    # Create a mapping from the original gameid to a smaller integer id
    unique_game_ids = df["gameid"].unique()
    gameid_to_int = {gameid: idx for idx, gameid in enumerate(unique_game_ids)}
    # Replace the gameid in the DataFrame with the smaller integer id
    df["gameid"] = df["gameid"].map(gameid_to_int)

    df.drop(columns=["playerid", "teamid"], axis=1, inplace=True)
    df.drop(
        columns=[
            "opp_csat25",
            "golddiffat25",
            "xpdiffat25",
            "csdiffat25",
            "killsat25",
            "assistsat25",
            "deathsat25",
            "opp_killsat25",
            "opp_assistsat25",
            "opp_deathsat25",
            "dragons (type unknown)",
        ],
        axis=1,
        inplace=True,
    )

    teams = df.query("position == 'team'")
    players = df.query("position != 'team'")

    players.to_csv("database/players.csv", index=False)
    teams.to_csv("database/teams.csv", index=False)
    df.to_csv("database/data_treated.csv", index=False)


if __name__ == "__main__":
    download_csv_files()

    combine_dfs(2024, 2025)
    treat_data()
