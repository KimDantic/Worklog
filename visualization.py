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
    combined_df['task_wo_punct'] = combined_df['task'].apply(lambda x: ''.join([char for char in str(x) if char not in string.punctuation]))

    # Text preprocessing
    stopword = nltk.corpus.stopwords.words('english')
    lemmatizer = WordNetLemmatizer()
    combined_df['task_processed'] = combined_df['task_wo_punct'].apply(lambda x: ' '.join([lemmatizer.lemmatize(word) for word in x.lower().split() if word not in stopword]))

    return combined_df

# Load the data
combined_df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
filter_type = st.sidebar.selectbox("Filter Type", ["Date", "Category", "Full Name", "Search Term"])

if filter_type == "Date":
    date_filter = st.sidebar.date_input("Select Date Range", [])
    if len(date_filter) == 2:
        combined_df = combined_df[(combined_df['started_at'] >= pd.to_datetime(date_filter[0])) & (combined_df['started_at'] <= pd.to_datetime(date_filter[1]))]

elif filter_type == "Category":
    search_term = st.sidebar.text_input("Search Category")
    if search_term:
        combined_df = combined_df[combined_df['task_processed'].str.contains(search_term, case=False)]

elif filter_type == "Full Name":
    full_name_filter = st.sidebar.multiselect("Filter by Full Name", options=combined_df['Full_Name'].unique())
    if full_name_filter:
        combined_df = combined_df[combined_df['Full_Name'].isin(full_name_filter)]

elif filter_type == "Search Term":
    search_term = st.sidebar.text_input("Search Task")
    if search_term:
        combined_df = combined_df[combined_df['task_processed'].str.contains(search_term, case=False)]

# Visualization: Word Cloud
st.subheader("Most Common Words - Word Cloud")
all_words = ' '.join(combined_df['task_processed'].tolist())
wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='Oranges').generate(all_words)

fig, ax = plt.subplots()
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis("off")
plt.tight_layout(pad=0)
st.pyplot(fig)
