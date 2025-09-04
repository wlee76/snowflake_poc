import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from snowflake.snowpark.context import get_active_session


# Initialize Snowflake session
def create_snowflake_session():
    return Session.builder.configs(st.secrets["snowflake"]).create()

try:
    #session = create_snowflake_session()
## Get the current credentials
    session = get_active_session()
except Exception as e:
    st.error(f"Failed to connect to Snowflake: {e}")
    st.stop()

# Sample table and data (replace with your actual table and data)
table_name = "HOLDINGS"
sample_data = {"col1": ["A", "B", "C"], "col2": [1, 2, 3]}
df = pd.DataFrame(sample_data)

# Function to load data from Snowflake
def load_data(table_name):
    try:
        snow_df = session.table(table_name)
        pdf = snow_df.to_pandas()
        return pdf
    except Exception as e:
        st.error(f"Error loading data from Snowflake: {e}")
        return pd.DataFrame()

# Function to write data back to Snowflake
def write_data(table_name, data):
    try:
        session.write_pandas(data, table_name, overwrite=True)
        st.success("Data successfully written to Snowflake!")
    except Exception as e:
        st.error(f"Error writing data to Snowflake: {e}")

# Streamlit app
st.title("Snowflake Write-Back Example")

# Load data from Snowflake
data = load_data(table_name)

# Display data
st.write("Current Data:")
st.dataframe(data)

# Input form for new data
st.subheader("Add New Data")
col1_input = st.text_input("Enter value for col1")
col2_input = st.number_input("Enter value for col2", value=0)

if st.button("Add Data"):
    new_data = pd.DataFrame({"col1": [col1_input], "col2": [col2_input]})
    updated_data = pd.concat([data, new_data], ignore_index=True)
    write_data(table_name, updated_data)
    data = load_data(table_name)  # Refresh data
    st.dataframe(data) # Display refreshed data
    
# Close the session
session.close()