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

# Theme toggle
theme = st.sidebar.radio("Select Theme", ["Dark", "Light"], index=0)

# Applying theme
if theme == "Dark":
    st.markdown("<style>body {background-color: #121212; color: #FFFFFF;}</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>body {background-color: #FFFFFF; color: #000000;}</style>", unsafe_allow_html=True)

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

# Sidebar filters
st.sidebar.header("Filters")
filter_type = st.sidebar.multiselect("Filter Type", ["Date", "Category", "Full Name", "Search Term"], default=["Search Term"])

if "Date" in filter_type:
    date_filter = st.sidebar.date_input("Select Date Range", [])
    if len(date_filter) == 2:
        combined_df = combined_df[(combined_df['started_at'] >= pd.to_datetime(date_filter[0])) & (combined_df['started_at'] <= pd.to_datetime(date_filter[1]))]

if "Category" in filter_type:
    search_term = st.sidebar.text_input("Search Category")
    if search_term:
        combined_df = combined_df[combined_df['task_processed'].str.contains(search_term, case=False)]

if "Full Name" in filter_type:
    full_name_filter = st.sidebar.multiselect("Filter by Full Name", options=combined_df['Full_Name'].unique())
    if full_name_filter:
        combined_df = combined_df[combined_df['Full_Name'].isin(full_name_filter)]

if "Search Term" in filter_type:
    search_term = st.sidebar.text_input("Search Task")
    if search_term:
        combined_df = combined_df[combined_df['task_processed'].str.contains(search_term, case=False)]

# Visualization type
st.subheader("Word Visualization")
vis_type = st.selectbox("Select Visualization Type", ["Word Cloud", "Bar Chart", "Pie Chart"], index=0)

if vis_type == "Word Cloud":
    all_words = ' '.join(combined_df['task_processed'].tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='black' if theme == "Dark" else 'white').generate(all_words)
    st.image(wordcloud.to_array())

elif vis_type == "Bar Chart":
    word_counts = Counter(' '.join(combined_df['task_processed']).split()).most_common(20)
    df_plot = pd.DataFrame(word_counts, columns=['Word', 'Count'])
    fig = px.bar(df_plot, x='Word', y='Count', title="Top 20 Most Common Words")
    st.plotly_chart(fig)

elif vis_type == "Pie Chart":
    word_counts = Counter(' '.join(combined_df['task_processed']).split()).most_common(10)
    df_plot = pd.DataFrame(word_counts, columns=['Word', 'Count'])
    fig = px.pie(df_plot, names='Word', values='Count', title="Top 10 Most Common Words")
    st.plotly_chart(fig)
