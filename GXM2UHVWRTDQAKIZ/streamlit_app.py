import streamlit as st

st.set_page_config(page_title="Ashmore Bug report", layout="centered")

session = st.connection('snowflake').session()

# Change the query to point to your table
def get_data(_session):
    query = """
    select * from WESTEST.IMPACT.BUG_REPORT_DATA
    order by date desc
    limit 100
    """
    data = _session.sql(query).collect()
    return data

# Change the query to point to your table
def add_row_to_db(session, row):
    sql = f"""INSERT INTO WESTEST.IMPACT.BUG_REPORT_DATA VALUES
    ('{row['author']}',
    '{row['bug_type']}',
    '{row['comment']}',
    '{row['date']}',
    '{row['bug_severity']}')"""

    session.sql(sql).collect()

st.title("Ashmore Bug report demo!")

st.sidebar.write(
    f"This app demos how to read and write data from a Snowflake Table"
)

form = st.form(key="annotation", clear_on_submit=True)

with form:
    cols = st.columns((1, 1))
    author = cols[0].text_input("Report author:")
    bug_type = cols[1].selectbox(
        "Bug type:", ["Front-end", "Back-end", "Data related", "404"], index=2
    )
    comment = st.text_area("Comment:")
    cols = st.columns(2)
    date = cols[0].date_input("Bug date occurrence:")
    bug_severity = cols[1].slider("Bug priority :", 1, 5, 2)
    submitted = st.form_submit_button(label="Submit")

if submitted:
    try:
        add_row_to_db(
            session,
            {'author':author,
            'bug_type': bug_type,
            'comment':comment,
            'date':str(date),
            'bug_severity':bug_severity
        })
        st.success("Thanks! Your bug was recorded in the database.")
        st.balloons()
    except Exception as e:
        st.error(f"An error occurred: {e}")

expander = st.expander("See 100 most recent records")
with expander:
    st.dataframe(get_data(session))