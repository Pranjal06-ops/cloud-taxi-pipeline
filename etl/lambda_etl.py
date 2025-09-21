"""AWS Lambda ETL (also runnable locally)

Behavior:
- If running in AWS Lambda, set env vars: BUCKET_NAME, FILE_KEY, DB_HOST, DB_NAME, DB_USER, DB_PASS
- If running locally, set LOCAL_FILE and provide DB env vars, or use CLI helper run_local_etl.py
"""
import os
import boto3
import pandas as pd
from sqlalchemy import create_engine, text

def read_csv_from_s3(bucket, key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(obj['Body'])

def read_csv_local(path):
    return pd.read_csv(path)

def clean_df(df):
    # Basic cleaning steps
    df = df.dropna()
    # Ensure numeric columns are correct type
    for col in ['trip_distance','fare_amount','tip_amount','total_amount','passenger_count','vendor_id','trip_id','pickup_location_id','dropoff_location_id']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    # Parse datetimes
    for col in ['pickup_datetime','dropoff_datetime']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    df = df.dropna()
    return df

def load_to_postgres(df, db_uri, table_name='trips'):
    engine = create_engine(db_uri)
    # Create table if not exists via a safe approach using SQL - keep schema controlled in scripts/create_db.sql
    # Use to_sql for convenience (append)
    df.to_sql(table_name, engine, if_exists='append', index=False, method='multi', chunksize=1000)
    engine.dispose()

def handler(event=None, context=None):
    # Determine environment
    bucket = os.environ.get('BUCKET_NAME')
    key = os.environ.get('FILE_KEY')
    local_file = os.environ.get('LOCAL_FILE')

    if bucket and key:
        df = read_csv_from_s3(bucket, key)
    elif local_file:
        df = read_csv_local(local_file)
    else:
        raise ValueError('No source provided. Set BUCKET_NAME+FILE_KEY or LOCAL_FILE.')

    df = clean_df(df)

    # DB connection
    db_host = os.environ['DB_HOST']
    db_name = os.environ.get('DB_NAME','taxi')
    db_user = os.environ['DB_USER']
    db_pass = os.environ['DB_PASS']
    db_port = os.environ.get('DB_PORT','5432')

    db_uri = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    load_to_postgres(df, db_uri)
    return {'status': 'success', 'rows': len(df)}

# Lambda entrypoint
def lambda_handler(event, context):
    return handler(event, context)

if __name__ == '__main__':
    # Quick local run for testing
    os.environ.setdefault('LOCAL_FILE', '../data/nyc_taxi_sample.csv')
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_NAME', 'taxi')
    os.environ.setdefault('DB_USER', 'postgres')
    os.environ.setdefault('DB_PASS', 'postgres')
    print(handler())
