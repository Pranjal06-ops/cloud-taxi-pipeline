"""Local ETL helper to load CSV into Postgres (useful for local testing using Docker)"""
import argparse
import os
from sqlalchemy import create_engine
import pandas as pd

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--file', required=True, help='Path to CSV file')
    p.add_argument('--db-host', default='localhost')
    p.add_argument('--db-port', default='5432')
    p.add_argument('--db-name', default='taxi')
    p.add_argument('--db-user', default='postgres')
    p.add_argument('--db-pass', default='postgres')
    return p.parse_args()

def main():
    args = parse_args()
    df = pd.read_csv(args.file)
    df = df.dropna()
    engine = create_engine(f'postgresql://{args.db_user}:{args.db_pass}@{args.db_host}:{args.db_port}/{args.db_name}')
    df.to_sql('trips', engine, if_exists='append', index=False, method='multi', chunksize=500)
    engine.dispose()
    print(f'Loaded {len(df)} rows into trips table.')

if __name__ == '__main__':
    main()
