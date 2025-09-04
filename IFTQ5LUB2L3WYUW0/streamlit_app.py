import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from datetime import timedelta

st.set_page_config(page_title="Ashmore report", layout="centered")
st.header("Cumulative Stats")


session = st.connection('snowflake').session()


# Helper functions
def format_with_commas(number):
    return f"{number:,}"

def aggregate_data(df, freq):
    return df.resample(freq, on='DATE').agg({
        'VIEWS': 'sum',
        'WATCH_HOURS': 'sum',
        'NET_SUBSCRIBERS': 'sum',
        'LIKES': 'sum'
    }).reset_index()

def create_chart(y, color, height, chart_type):
    if chart_type=='Bar':
        st.bar_chart(df_display, x="DATE", y=y, color=color, height=height)
    if chart_type=='Area':
        st.area_chart(df_display, x="DATE", y=y, color=color, height=height)


def get_ashmore_data(_session):
    query = """
    select * from WESTEST.IMPACT.HOLDINGS
    order by ANALYSIS_DATE desc
    limit 100
    """
    data = _session.sql(query).collect()
    return data


# Create DataFrame
df = pd.DataFrame()
df = get_ashmore_data(session)


#df =  get_ashmore_data()

# Input widgets
# Date range selection
#col = st.columns(4)
#with col[0]:
    #start_date = st.date_input("Start date", df['ANALYSIS_DATE'].min().date())
    #start_date = df['ANALYSIS_DATE'].min().date()
#with col[1]:
#    end_date = st.date_input("End date", df['ANALYSIS_DATE'].max().date())
# Time frame selection
#with col[2]:
    #time_frame = st.selectbox("Select time frame",
    #    ("Daily", "Weekly", "Monthly", "Quarterly")    )
# Chart type
#with col[3]:
#    chart_selection = st.selectbox("Select a chart type ("Bar", "Area"))

#start_date = df['ANALYSIS_DATE'].min().date()
#end_date = df['ANALYSIS_DATE'].max().date()
expander = st.expander("See 100 most recent records")
with expander:
    st.dataframe(get_ashmore_data(session))
st.divider()




# Filter data based on date range
mask = (df['ANALYSIS_DATE'].dt.date >= start_date) & (df['ANALYSIS_DATE'].dt.date <= end_date)
df_filtered = df.loc[mask]

# Aggregate data based on selected time frame
if time_frame == 'Daily':
    df_display = df_filtered
elif time_frame == 'Weekly':
    df_display = aggregate_data(df_filtered, 'W-MON')
elif time_frame == 'Monthly':
    df_display = aggregate_data(df_filtered, 'ME')
elif time_frame == 'Quarterly':
    df_display = aggregate_data(df_filtered, 'QE')


# Compute metric growth based on selected time frame
if len(df_display) >= 2:
    subscribers_growth = int(df_display.NET_SUBSCRIBERS.iloc[-1] - df_display.NET_SUBSCRIBERS.iloc[-2])
    views_growth = int(df_display.VIEWS.iloc[-1] - df_display.VIEWS.iloc[-2])
    watch_hours_growth = int(df_display.WATCH_HOURS.iloc[-1] - df_display.WATCH_HOURS.iloc[-2])
    likes_growth = int(df_display.LIKES.iloc[-1] - df_display.LIKES.iloc[-2])
else:
    subscribers_growth = views_growth = watch_hours_growth = likes_growth = 0


# Create metrics columns
cols = st.columns(4)
with cols[0]:
    st.metric("Subscribers", 
              format_with_commas(df_display.NET_SUBSCRIBERS.sum()),
              format_with_commas(subscribers_growth)
             )
    create_chart(y="NET_SUBSCRIBERS", color="#29B5E8", height=200, chart_type=chart_selection)
with cols[1]:
    st.metric("Views", 
              format_with_commas(df_display.VIEWS.sum()), 
              format_with_commas(views_growth)
             )
    #st.bar_chart(df_display, x="DATE", y="VIEWS", color="#FF9F36", height=200)
    create_chart(y="VIEWS", color="#FF9F36", height=200, chart_type=chart_selection)
with cols[2]:
    st.metric("Watch Hours", 
              format_with_commas(df_display.WATCH_HOURS.sum()), 
              format_with_commas(watch_hours_growth)
             )
    #st.bar_chart(df_display, x="DATE", y="WATCH_HOURS", color="#D45B90", height=200)
    create_chart(y="WATCH_HOURS", color="#D45B90", height=200, chart_type=chart_selection)
with cols[3]:
    st.metric("Likes", 
              format_with_commas(df_display.LIKES.sum()), 
              format_with_commas(likes_growth)
             )
    #st.bar_chart(df_display, x="DATE", y="LIKES", color="#7D44CF", height=200)
    create_chart(y="LIKES", color="#7D44CF", height=200, chart_type=chart_selection)


# Display filtered DataFrame
with st.expander("See filtered data"):
    st.dataframe(df_display)