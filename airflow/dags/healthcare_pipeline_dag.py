from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="healthcare_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    ingest = BashOperator(
        task_id="ingest_data",
        bash_command="python /opt/project/scripts/upload_to_bigquery.py"
    )

    dbt_run = BashOperator(
        task_id="run_dbt",
        bash_command="cd /opt/project/dbt && dbt run"
    )

    dbt_test = BashOperator(
        task_id="test_dbt",
        bash_command="cd /opt/project/dbt && dbt test"
    )

    ingest >> dbt_run >> dbt_test