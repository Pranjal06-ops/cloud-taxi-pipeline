# ☁️ Cloud Data Pipeline & Dashboard – NYC Taxi Data

This repository is a end-to-end cloud data pipeline example. It ingests raw taxi trip CSV files, transforms data, loads it to Postgres, and provides an interactive Streamlit dashboard.

## What's included (ready-to-run)
- `data/nyc_taxi_sample.csv` — sample dataset (small).
- `etl/` — ETL scripts: `lambda_etl.py` (runnable locally or as AWS Lambda), `run_local_etl.py` (local helper).
- `dashboard/` — Streamlit dashboard (`app.py`).
- `sql/` — useful queries.
- `scripts/create_db.sql` — DB schema.
- `docker-compose.yml` — run Postgres locally for testing.
- `requirements.txt` — Python dependencies.

---

## Quick start — Local (recommended for testing)
1. Install Docker & Docker Compose.
2. Start a local Postgres:
   ```bash
   docker-compose up -d
   ```
3. (Optional) Create the `trips` table:
   ```bash
   docker exec -it $(docker ps -q -f "ancestor=postgres:15") psql -U postgres -d taxi -c "CREATE TABLE IF NOT EXISTS trips (trip_id INT PRIMARY KEY, vendor_id INT, pickup_datetime TIMESTAMP, dropoff_datetime TIMESTAMP, passenger_count INT, trip_distance FLOAT, pickup_location_id INT, dropoff_location_id INT, payment_type VARCHAR(20), fare_amount FLOAT, tip_amount FLOAT, total_amount FLOAT);"
   ```
4. Install Python dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
5. Load sample data locally:
   ```bash
   python etl/run_local_etl.py --file data/nyc_taxi_sample.csv --db-host localhost --db-port 5432 --db-name taxi --db-user postgres --db-pass postgres
   ```
6. Launch the dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```
   Open the URL shown (usually http://localhost:8501).

---

## Deploying to AWS (high-level steps)
You can deploy a cloud version using AWS S3, Lambda, and RDS:

### 1) S3 — upload raw CSV
- Create an S3 bucket (e.g., `my-taxi-data-bucket`).
- Upload `data/nyc_taxi_sample.csv`.

### 2) RDS — Postgres
- Create an RDS Postgres instance.
- Make the DB accessible from your environment (set security group to allow your IP for testing).
- Run `scripts/create_db.sql` to create the `trips` table.

### 3) Lambda — ETL
- Option A (recommended): Build a Lambda **container image** including pandas and dependencies. Push to ECR and create Lambda with that image.
- Option B: Create a Lambda with a custom layer containing pandas/psycopg2 (advanced).
- Set Lambda environment variables: `BUCKET_NAME`, `FILE_KEY`, `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`.
- Grant Lambda an IAM policy with `s3:GetObject` and CloudWatch Logs access.

Sample IAM policy (S3 + Logs):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::YOUR_BUCKET_NAME/*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": ["arn:aws:logs:*:*:*"]
    }
  ]
}
```

### 4) Streamlit — Dashboard
- You can deploy `dashboard/app.py` to **Streamlit Community Cloud** (free for public repos) or an EC2 instance.
- If using Streamlit Cloud: add database credentials under **Repository Settings → Secrets** (keys: DB_HOST, DB_NAME, DB_USER, DB_PASS).
- If using EC2, set environment variables or use a secrets manager.

---

## Notes & Troubleshooting
- **Lambda packaging:** pandas & psycopg2 are large; use Lambda container images (recommended). See AWS docs for building Python Lambda images.
- **Security:** For production, do NOT make RDS publicly accessible; place Lambda in the same VPC or use RDS proxy.
- **Scaling:** For larger datasets, consider processing via AWS Glue or EMR and using Redshift for analytics.

---

## License
MIT
