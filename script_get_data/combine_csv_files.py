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
            year = int(os.path.basename(file).split('_')[0])
        except (ValueError, IndexError):
            print(f"Could not extract year from filename: {file}")
            continue
            
        # Check if year is within the specified range
        if start_year <= year <= end_year:
            print(f"Processing data for year {year}...")
            try:
                df = pd.read_csv(file)
                # Add year column if it doesn't exist
                if 'year' not in df.columns:
                    df['year'] = year
                dfs.append(df)
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
    
    if not dfs:
        raise ValueError(f"No data found for the specified range {start_year}-{end_year}")
    
    # Combine all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Sort by date if a date column exists
    date_columns = ['date', 'game_date', 'match_date']
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

if __name__ == "__main__":
    # Example usage
    try:
        # You can modify these years as needed
        start_year = 2014
        end_year = 2025
        
        print(f"Combining data from {start_year} to {end_year}...")
        combined_df = combine_csv_files(start_year, end_year)
        
        print(f"\nTotal rows in combined dataset: {len(combined_df)}")
        print("\nColumns in the dataset:")
        print(combined_df.columns.tolist())
        
        # Save the combined data
        save_combined_data(combined_df)
        
    except Exception as e:
        print(f"Error: {str(e)}") 