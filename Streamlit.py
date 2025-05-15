import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="GitHub Data Visualization", layout="wide")
st.markdown("<style>body { background-color: black; }</style>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("GitHub Data Visualization")
github_url = st.sidebar.text_input("Enter GitHub URL:", "https://github.com/KimDantic/Worklog")

# Load data from GitHub
@st.cache_data
def load_data(url):
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Process GitHub URL to access raw CSV
if github_url:
    raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    data = load_data(raw_url)

    if data is not None:
        st.write("## Data Preview")
        st.dataframe(data.head())

        # Simple Data Visualization
        st.write("## Data Visualization")
        fig, ax = plt.subplots()
        data.hist(ax=ax, figsize=(10, 6))
        st.pyplot(fig)
