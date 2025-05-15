import requests
import pandas as pd

# GitHub repository details
repo_owner = "KimDantic"
repo_name = "Worklog"
branch = "main"  # Change if your branch is not "main"

# GitHub API URL
api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/"

# Fetch the list of files in the repository
response = requests.get(api_url)
response.raise_for_status()  # Raise an error if the request fails
files = response.json()

# Filter for CSV files
csv_files = [(file['name'], file['download_url']) for file in files if file['name'].endswith('.csv')]

# Check if any CSV files are found
if not csv_files:
    print("No CSV files found in the repository.")
else:
    print("CSV files found:")
    for filename, url in csv_files:
        print(f" - {filename}")

    # Read each CSV file into a list of DataFrames
    dataframes = []
    for filename, url in csv_files:
        print(f"Reading file: {filename}")

        # Extract the numeric part from the filename
        parts = filename.split('-')
        numeric_id = parts[2] if len(parts) > 2 else 'unknown'

        # Read the CSV and add the numeric_id as a new column
        df = pd.read_csv(url)
        df['FileID'] = numeric_id  # Add new column with the extracted numeric part
        dataframes.append(df)

    # Combine all DataFrames into one (optional)
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Display the combined DataFrame
    print("\nCombined DataFrame:")
    print(combined_df)
