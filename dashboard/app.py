import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

st.set_page_config(page_title='NYC Taxi Cloud Dashboard', layout='wide')
st.title('🚕 NYC Taxi Data Dashboard (Cloud)')

@st.cache_data
def get_engine():
    # Use Streamlit secrets or environment variables
    db_host = st.secrets.get('DB_HOST', os.environ.get('DB_HOST'))
    db_name = st.secrets.get('DB_NAME', os.environ.get('DB_NAME', 'taxi'))
    db_user = st.secrets.get('DB_USER', os.environ.get('DB_USER'))
    db_pass = st.secrets.get('DB_PASS', os.environ.get('DB_PASS'))
    db_port = st.secrets.get('DB_PORT', os.environ.get('DB_PORT', '5432'))
    if not all([db_host, db_user, db_pass]):
        st.error('Database credentials not found. Please configure st.secrets or environment variables.')
        st.stop()
    uri = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    return create_engine(uri)

engine = get_engine()

@st.cache_data
def load_sample(limit=500):
    query = f"SELECT * FROM trips LIMIT {limit};"
    df = pd.read_sql(query, engine)
    return df

df = load_sample()

st.subheader('Sample Data (first 10 rows)')
st.dataframe(df.head(10))

st.subheader('Average Fare by Passenger Count')
avg = df.groupby('passenger_count', dropna=True)['total_amount'].mean().reset_index()
st.bar_chart(avg.set_index('passenger_count'))

st.subheader('Trip Distance vs Fare')
st.altair_chart(
    st.altair_chart if False else None, use_container_width=True
)  # placeholder to avoid Altair requirement; using scatter with pandas
st.write('Showing scatter using dataframe (trip_distance vs fare_amount)')
st.write(df[['trip_distance', 'fare_amount']].dropna().sample(min(len(df), 200)))

st.subheader('Top Pickup Locations')
top_pickups = df.groupby('pickup_location_id')['trip_id'].count().reset_index().rename(columns={'trip_id':'count'}).sort_values('count', ascending=False).head(10)
st.table(top_pickups)
