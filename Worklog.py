import streamlit as st
import pandas as pd
import requests
import os

# Attempting to import matplotlib, handling if not installed
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

st.title("GitHub CSV Data Visualizer")

# GitHub repo details
repo_owner = "romero220"
repo_name = "projectmanagement"
branch = "main"
token = os.getenv("GITHUB_TOKEN")  # Ensure your token is stored in an environment variable

api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/"
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    files = response.json()

    # Filter CSV files
    csv_files = [(file['name'], file['download_url']) for file in files if file['name'].endswith('.csv')]

    if not csv_files:
        st.error("No CSV files found in the repository.")
    else:
        dataframes = []

        for filename, url in csv_files:
            st.write(f"Reading file: {filename}")
            numeric_id = filename.split('-')[2] if '-' in filename else 'Unknown'
            df = pd.read_csv(url)
            df['FileID'] = numeric_id
            dataframes.append(df)

        combined_df = pd.concat(dataframes, ignore_index=True)

        # Ensure columns exist
        required_columns = ['Issue', 'Category']
        if all(col in combined_df.columns for col in required_columns):
            data = combined_df[required_columns].copy()
            data.columns = ['text', 'label']

            st.write("### Data Loaded Successfully")
            st.dataframe(data)

            # Visualization
            if plt:
                st.write("### Data Visualization")
                category_counts = data['label'].value_counts()
                fig, ax = plt.subplots()
                category_counts.plot(kind='bar', ax=ax)
                ax.set_title('Category Distribution')
                ax.set_xlabel('Category')
                ax.set_ylabel('Count')
                st.pyplot(fig)
            else:
                st.warning("Matplotlib is not installed. Please run: pip install matplotlib")

        else:
            st.error(f"Missing columns: {required_columns}")

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to GitHub: {str(e)}")
