import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="GitHub Data Visualization", layout="wide")
st.markdown("<style>body { background-color: black; }</style>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("GitHub Data Visualization")
github_url = "https://raw.githubusercontent.com/KimDantic/Worklog/main/your_data_file.csv"  # Use your exact CSV file path

# Load data from GitHub
@st.cache_data
def load_data(url):
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load data directly from GitHub
data = load_data(github_url)

if data is not None:
    st.write("## Data Preview")
    st.dataframe(data.head())

    # Simple Data Visualization
    st.write("## Data Visualization")
    fig, ax = plt.subplots()
    data.hist(ax=ax, figsize=(10, 6))
    st.pyplot(fig)
