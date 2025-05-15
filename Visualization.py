import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import os
import warnings
import string
import re
import nltk
from nltk.stem import WordNetLemmatizer
import plotly.express as px

# Ensure NLTK resources are downloaded
nltk.download('stopwords')
nltk.download('wordnet')

warnings.filterwarnings("ignore", message="Converting to PeriodArray/Index representation will drop timezone information")

# Streamlit page configuration
st.set_page_config(page_title="Task Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    csv_files = [file for file in os.listdir('.') if file.endswith('.csv')]

    if not csv_files:
        st.warning("No CSV files found in the repository.")
        return pd.DataFrame()

    dataframes = []
    for filename in csv_files:
        df = pd.read_csv(filename)
        numeric_id = filename.split('-')[2] if '-' in filename else 'Unknown'
        df['ProjectID'] = numeric_id
        dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)

    combined_df['ProjectID-ID'] = combined_df['ProjectID'].astype(str) + "-" + combined_df['id'].astype(str)
    combined_df['Full_Name'] = combined_df['user_first_name'].astype(str) + " " + combined_df['user_last_name'].astype(str)

    combined_df['started_at'] = pd.to_datetime(combined_df['started_at'], errors="coerce")
    combined_df['week'] = combined_df['started_at'].dt.isocalendar().week
    combined_df['month'] = combined_df['started_at'].dt.month
    combined_df['year'] = combined_df['started_at'].dt.year
    combined_df['year_month'] = combined_df['started_at'].dt.to_period("M")

    combined_df['task_wo_punct'] = combined_df['task'].astype(str).apply(lambda x: ''.join([c for c in x if c not in string.punctuation]))
    combined_df['task_wo_punct_split'] = combined_df['task_wo_punct'].str.lower().str.split(r'\W+')

    stopword = nltk.corpus.stopwords.words('english')
    combined_df['task_wo_punct_split_wo_stopwords'] = combined_df['task_wo_punct_split'].apply(lambda x: [w for w in x if w and w not in stopword])

    lemmatizer = WordNetLemmatizer()
    combined_df['task_wo_punct_split_wo_stopwords_lemmatized'] = combined_df['task_wo_punct_split_wo_stopwords'].apply(lambda x: [lemmatizer.lemmatize(word) for word in x])

    combined_df["Hours"] = combined_df["minutes"] / 60

    categories = {
        "technology": ["website", "sql", "backend", "repository", "ai", "coding", "file", "database", "application", "program", "flask", "html", "css", "javascript"],
        "actions": ["reviewed", "created", "tested", "fixed", "debugged", "implemented", "researched", "planned", "updated", "designed", "documented", "analyzed", "optimized", "added", "removed"],
        "design": ["logo", "design", "styling", "layout", "responsive", "theme", "navbar", "icon", "image", "photo", "redesigning", "wireframes"],
        "writing": ["blog", "guide", "documentation", "report", "note", "summary", "draft", "content", "copywriting"],
        "meetings": ["meeting", "call", "discussion", "session", "presentation", "team"],
        "business": ["grant", "funding", "startup", "loan", "entrepreneur", "business", "government"],
        "errors": ["bug", "error", "issue", "fixing", "debugging", "problem", "mistake"],
        "time": ["hour", "day", "week", "month", "year"],
        "miscellaneous": []
    }

    def categorize_words(words, categories):
        matched_categories = set()
        for word in words:
            found = False
            for category, keywords in categories.items():
                if word in keywords:
                    matched_categories.add(category)
                    found = True
                    break
            if not found:
                matched_categories.add("miscellaneous")
        return list(matched_categories)

    combined_df['Categorized'] = combined_df['task_wo_punct_split_wo_stopwords_lemmatized'].apply(lambda x: categorize_words(x, categories))

    return combined_df

combined_df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
categories_filter = st.sidebar.multiselect("Select Categories", options=sorted(combined_df['Categorized'].explode().dropna().unique()))
date_filter = st.sidebar.date_input("Filter by Date", [])
search_term = st.sidebar.text_input("Search Task", "")
full_name_filter = st.sidebar.multiselect("Filter by Full Name", options=sorted(combined_df['Full_Name'].unique()))

filtered_data = combined_df.copy()

if categories_filter:
    filtered_data = filtered_data[filtered_data['Categorized'].apply(lambda cats: any(c in cats for c in categories_filter))]

if len(date_filter) == 2:
    start_date, end_date = pd.to_datetime(date_filter[0]), pd.to_datetime(date_filter[1])
    filtered_data = filtered_data[(filtered_data['started_at'] >= start_date) & (filtered_data['started_at'] <= end_date)]

if search_term:
    filtered_data = filtered_data[filtered_data['task'].str.contains(search_term, case=False, na=False)]

if full_name_filter:
    filtered_data = filtered_data[filtered_data['Full_Name'].isin(full_name_filter)]

csv_data = filtered_data.to_csv(index=False).encode('utf-8')

st.sidebar.download_button(
    label="📥 Download Filtered CSV",
    data=csv_data,
    file_name="filtered_data.csv",
    mime="text/csv"
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Overview", "Hours", "Entries", "Task Overtime", "5", "6", "7"])

# Tab 1: Overview
with tab1:
    st.subheader("Preview of Filtered Data (First 100 Rows)")
    st.dataframe(filtered_data.head(100), use_container_width=True)

    st.subheader("Missing Values by Column")
    missing_counts = filtered_data.isnull().sum()
    missing_counts = missing_counts[missing_counts > 0].sort_values(ascending=False)
    if not missing_counts.empty:
        missing_df = pd.DataFrame({'Column': missing_counts.index, 'Missing Values': missing_counts.values})
        fig_missing = px.bar(
            missing_df,
            x='Column',
            y='Missing Values',
            color='Missing Values',
            color_continuous_scale='Reds',
            title="Number of Missing Values per Column",
            labels={'Missing Values': 'Count of NaNs'}
        )
        fig_missing.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_missing, use_container_width=True)
    else:
        st.success("No missing values found in the filtered dataset.")

    all_words = [word for sublist in filtered_data['task_wo_punct_split_wo_stopwords_lemmatized'] for word in sublist]
    word_counts = Counter(all_words).most_common(20)
    if word_counts:
        words, counts = zip(*word_counts)
        df_plot = pd.DataFrame({'Word': words, 'Count': counts})
        fig = px.bar(
            df_plot,
            x='Word',
            y='Count',
            color='Count',
            color_continuous_scale='Oranges',
            title="Top 20 Most Common Words (Lemmatized)",
            labels={'Count': 'Frequency'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.bar(title="Top 20 Most Common Words (Lemmatized)")
        fig.update_layout(
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': "No data available",
                'xref': "paper",
                'yref': "paper",
                'showarrow': False,
                'font': {'size': 16}
            }]
        )
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Hours by Time Period
with tab2:
    st.header("Hours by Time Period")
    time_option = st.selectbox("Select Time Period", options=["Week", "Month", "Year"], index=2, key="time_period_tab2")

    time_col = {"Week": "week", "Month": "month", "Year": "year"}[time_option]

    grouped_data = filtered_data.groupby([time_col, 'Full_Name'], as_index=False)['Hours'].sum()
    fig = px.bar(
        grouped_data,
        x=time_col,
        y='Hours',
        color='Full_Name',
        barmode='group',
        title=f"Hours by {time_option}",
        labels={time_col: time_option, 'Hours': 'Total Hours', 'Full_Name': 'User'},
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig.update_layout(
        plot_bgcolor='white',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 3: Entries Count
with tab3:
    st.header("Entries Count by Time Period")
    counts_time_option = st.selectbox("Select Time Period", options=["Week", "Month", "Year"], index=1)

    if counts_time_option == "Week":
        count_col = "week"
    elif counts_time_option == "Month":
        count_col = "year_month"
    else:
        count_col = "year"

    counts = filtered_data.groupby(count_col)['ProjectID-ID'].nunique().reset_index(name='Unique Entries')

    # For period (year_month), convert to string for better x-axis display
    if count_col == 'year_month':
        counts[count_col] = counts[count_col].astype(str)

    fig = px.bar(
        counts,
        x=count_col,
        y='Unique Entries',
        color='Unique Entries',
        color_continuous_scale='Oranges',
        title=f"Unique Entries by {counts_time_option}",
        labels={count_col: counts_time_option, 'Unique Entries': 'Unique Entries'}
    )
    fig.update_layout(xaxis_tickangle=-45, plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

# Tab 4: Task Overtime
with tab4:
    st.header("Task Overtime")
    time_option_tab4 = st.selectbox("Select Time Period", options=["Week", "Month", "Year"], index=2, key="time_period_tab4")

    if time_option_tab4 == "Week":
        filtered_data['week_start_date'] = filtered_data['started_at'].dt.to_period('W').apply(lambda r: r.start_time)
        time_col_tab4 = 'week_start_date'
        # For better axis labels, convert datetime to string
        filtered_data[time_col_tab4] = filtered_data[time_col_tab4].dt.strftime('%Y-%m-%d')
    elif time_option_tab4 == "Month":
        filtered_data['month_name'] = filtered_data['started_at'].dt.strftime('%B')
        filtered_data['month_order'] = filtered_data['started_at'].dt.month
        time_col_tab4 = 'month_name'
    else:
        filtered_data['year_str'] = filtered_data['year'].astype(str)
        time_col_tab4 = 'year_str'

    if time_option_tab4 == "Month":
        grouped_data = filtered_data.groupby([time_col_tab4, 'month_order', 'Full_Name'], as_index=False).size().rename(columns={'size': 'Entry_Count'})
        grouped_data = grouped_data.sort_values('month_order')
    else:
        grouped_data = filtered_data.groupby([time_col_tab4, 'Full_Name'], as_index=False).size().rename(columns={'size': 'Entry_Count'})

    fig = px.bar(
    grouped_data,
    x=time_col_tab4,
    y='Entry_Count',
    color='Full_Name',
    barmode='group',
    title=f"Task Entries Over Time by {time_option_tab4}",
    labels={time_col_tab4: time_option_tab4, 'Entry_Count': 'Task Entries', 'Full_Name': 'User'}
)
