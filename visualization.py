import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
import string
import re
import nltk
from nltk.stem import WordNetLemmatizer
import plotly.express as px
from wordcloud import WordCloud

# Ensure NLTK resources are downloaded
nltk.download('stopwords')
nltk.download('wordnet')

warnings.filterwarnings("ignore", message="Converting to PeriodArray/Index representation will drop timezone information")

# Streamlit page configuration
st.set_page_config(page_title="Task Dashboard", layout="wide")

# Applying dark theme directly
st.markdown("<style>body {background-color: #121212; color: #FFFFFF;}</style>", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    csv_files = [file for file in os.listdir('.') if file.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in the repository.")
        return pd.DataFrame()

    dataframes = []
    for filename in csv_files:
        df = pd.read_csv(filename)
        numeric_id = filename.split('-')[2] if '-' in filename else 'Unknown'
        df['ProjectID'] = numeric_id
        dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df['Full_Name'] = combined_df['user_first_name'].astype(str) + " " + combined_df['user_last_name'].astype(str)

    stopword = nltk.corpus.stopwords.words('english')
    lemmatizer = WordNetLemmatizer()
    combined_df['task_processed'] = combined_df['task'].astype(str).apply(lambda x: ' '.join([lemmatizer.lemmatize(word) for word in re.findall(r'\w+', x.lower()) if word not in stopword]))

    return combined_df

# Load the data
combined_df = load_data()

# Redesigned Sidebar Filters
st.sidebar.header("🔍 Filter Options")
st.sidebar.divider()
filter_type = st.sidebar.multiselect("🔖 Select Filter Type", ["Date", "Category", "Full Name", "Search Term"], default=["Search Term"])

# Choose Analysis
st.sidebar.header("📊 Choose Analysis")
analysis_type = st.sidebar.selectbox("Select Analysis Type", ["Word Cloud", "Tree Map", "Bar Chart", "Pie Chart"], index=0)

# Enhanced Tabs for Visualization
st.subheader("📊 Data Visualization")
tab1, tab2 = st.tabs(["Word Cloud", "Common Words Visualization"])

with tab1:
    all_words = ' '.join(combined_df['task_processed'].tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='black').generate(all_words)
    st.image(wordcloud.to_array())

with tab2:
    word_counts = Counter(' '.join(combined_df['task_processed']).split()).most_common(20)
    df_plot = pd.DataFrame(word_counts, columns=['Word', 'Count'])
    fig = px.treemap(df_plot, path=['Word'], values='Count', title="Top 20 Most Common Words")
    st.plotly_chart(fig)
