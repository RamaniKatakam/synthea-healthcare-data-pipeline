# Synthea Healthcare Data Pipeline (Airflow(Dockerized) + BigQuery + dbt)

An end-to-end ELT pipeline that processes synthetic patient records from [Synthea](https://synthetichealth.github.io/synthea/) and turns them into analytics-ready tables in BigQuery. The pipeline is orchestrated with Apache Airflow running in Docker, transformed with dbt, and visualized in Looker Studio.
This was built as a capstone project for the [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts/2026).

---

## Table of Contents

Healthcare organizations need reliable pipelines to:

* [Architecture](#architecture)
* [Tech Stack](#tech-stack)
* [Data Model](#data-model)
* [Pipeline Overview](#pipeline-overview)
* [Dashboard](#dashboard)
* [Reproducibility](#reproducibility)
* [Project Structure](#project-structure)
* [Design Decisions](#design-desicions)
* [What I'd Do Differently](#what-id-do-differently)

---

## Architecture

The pipeline follows a straightforward ELT pattern: raw CSV files land in BigQuery via a Python ingestion script, then dbt handles all the transformation logic across three layers (staging → intermediate → marts).

Data flows like this:

```
Synthea CSVs → Python script → BigQuery (raw) → dbt staging → dbt intermediate → dbt marts → Looker Studio
```
![Architecture Diagram](docs/architecture.png)

Everything is triggered and monitored through an Airflow DAG running locally in Docker.

---

## Tech Stack

###Layer                ###Tool

---
Data source             Synthea (synthetic EHR data)
Cloud data warehouse    Google BigQuery
Ingestion               Python (google-cloud-bigquery)
Transformation          dbt Core
OrchestrationApache     Airflow (Dockerized)
Visualization           Looker Studio

---

## Data Model

The mart layer follows a star schema. The central fact table is `fct_encounters`, which captures each patient visit along with its cost and associated condition. Two dimension tables hang off it:

```
dim_patient ──┐
              ├── fct_encounters
dim_condition─┘
```

* `dim_patient` — demographics, birth date, gender, computed age, and a lifetime cost rollup
* `dim_condition` — condition descriptions and codes linked to encounters
* `fct_encounters` — one row per encounter, with start/stop times, total claim cost, payer coverage, and foreign keys to both dimensions

---

## Pipeline Overview
### Airflow DAG
The `healthcare_pipeline` DAG runs three tasks in sequence:

1. `ingest_data` — runs `upload_to_bigquery.py`, which reads the Synthea CSVs and loads them into BigQuery using `WRITE_TRUNCATE`
2. `dbt_run` — executes all dbt models in dependency order
3. `dbt_test` — runs `not_null` and `unique` tests across the mart tables; the DAG fails here if data quality checks don't pass

### dbt Transformation Layers

**Staging** (`stg_*`) — one model per source table. The only work done here is renaming columns, casting types, and filtering out obviously bad rows. No joins.
**Intermediate** (`int_*`) — this is where the heavier logic lives. The main model here enriches each encounter with its condition details using a join between the encounters and conditions source tables. Deduplication also happens here.
**Marts** (`dim_*`, `fct_*`) — the final, business-ready models. These are what the dashboard queries.

---

## Dashboard
The Looker Studio dashboard surfaces three main views:
* **Patient Summary** — total visits and lifetime healthcare cost per patient, useful for identifying high-utilization cases
* **Condition Analysis** — the most frequently occurring conditions ranked by encounter count and total cost
* **Cost Trends** — aggregate spending over time, broken down by payer vs. out-of-pocket

---

## Reproducibility
The pipeline has two parts: cloud resources on GCP (BigQuery) and a local Airflow environment (Docker). You need to set up GCP first.

### 1. GCP Setup

**Create a GCP project** (or use an existing one) and note the project ID.
**Enable the BigQuery API:**
```
https://console.cloud.google.com/apis/library/bigquery.googleapis.com
```

**Create a service account:**

1. Go to IAM & Admin → Service Accounts → Create Service Account
2. Give it a name (e.g. `synthea-pipeline`)
3. Grant it the **BigQuery Admin** role
4. After creating, go to Keys → Add Key → Create New Key → JSON
5. Download the JSON file and save it somewhere safe — you'll need the path shortly

**Create a BigQuery dataset:**
```bash
bq --project_id=YOUR_PROJECT_ID mk synthea_healthcare
```
Or do it through the BigQuery console: your project → Create Dataset → name it `synthea_healthcare`, region of your choice.

---

### 2. Configure the Project
Clone the repo:
```bash
git clone https://github.com/RamaniKatakam/synthea-healthcare-data-pipeline.git
cd synthea-healthcare-data-pipeline
```
Copy the service account JSON key into the `config/` directory:
```bash
cp /path/to/your-key.json config/gcp_credentials.json
```
Update `config/config.yaml` with your GCP project ID and dataset name:
```yaml
gcp:
  project_id: YOUR_PROJECT_ID
  dataset: synthea_healthcare
  location: US
```
Update the dbt profile at `dbt/profiles/profiles.yml`:
```yaml
synthea_pipeline:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: YOUR_PROJECT_ID
      dataset: synthea_healthcare
      location: US
      keyfile: /opt/project/config/gcp_credentials.json
      threads: 4
      timeout_seconds: 300
```
---

### 3. Get the Synthea Data
Download the pre-generated CSV dataset:
```bash
# Option A: use the sample data included in the repo under data/ (small, ~100 patients)
# Option B: generate your own with Synthea
java -jar synthea-with-dependencies.jar -p 1000 --exporter.csv.export=true
cp output/csv/*.csv data/
```
---
### 4. Run Airflow
Make sure Docker and Docker Compose are installed, then:
```bash
docker-compose up --build
```
This starts the Airflow webserver and scheduler. Once it's up (takes about 30–60 seconds):

* Open `http://localhost:8080`
* Login: `admin` / `admin`
* Find the `healthcare_pipeline` DAG and toggle it on, or trigger it manually

The DAG will ingest the CSVs into BigQuery, run all dbt models, and run dbt tests. You can watch task progress in the Airflow UI.

---

### 5. Verify in BigQuery
After the DAG completes successfully, you should see these tables in your `synthea_healthcare` dataset:
```
stg_patients
stg_encounters
stg_conditions
int_encounter_conditions
dim_patient
dim_condition
fct_encounters
```
---

## Project Structure

```
synthea-healthcare-data-pipeline/
├── airflow/
│   └── dags/
│       └── healthcare_pipeline.py   # Main DAG definition
├── config/
│   ├── config.yaml                  # GCP project config
│   └── gcp_credentials.json         # ← you add this (not in git)
├── dashboards/
│   └── dashboard_overview.png       # Screenshot of Looker Studio dashboard
├── dbt/
│   ├── models/
│   │   ├── staging/                 # stg_* models
│   │   ├── intermediate/            # int_* models
│   │   └── marts/
│   │       ├── core/                # dim_* and fct_* tables
│   │       └── analytics/           # patient_summary, condition_analysis
│   ├── profiles/
│   │   └── profiles.yml             # BigQuery connection config
│   └── dbt_project.yml
├── docs/
│   ├── architecture.png             # Architecture diagram
│   ├── airflow_dag.png              # Screenshot of DAG graph
│   └── lineage/
│       └── lineage_full.png         # dbt lineage screenshot
├── scripts/
│   └── upload_to_bigquery.py        # Ingestion script
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Design Decisions
A few things worth explaining:

**Why incremental loading only on`fct_encounters`?** The dimensions (`dim_patient`, `dim_condition`) are small and cheap to rebuild from scratch. The fact table is where row counts grow over time, so that's where incremental loading actually matters.

**Why `WRITE_TRUNCATE` in the ingestion script?** For this project, the source data doesn't change — it's a one-time synthetic dataset. A full refresh on each run keeps things simple and idempotent. In a real pipeline with live EHR feeds, you'd want change detection here.

**Why not use Terraform?** The BigQuery dataset is the only cloud resource, and it's simple enough to create manually or via `bq mk`. Terraform would be the right call if the infrastructure were more complex (e.g. GCS buckets, Dataproc clusters, networking).

---

## What I'd Do Differently

If I were extending this project:

* Add **Slowly Changing Dimensions (Type 2)** for patient records, so changes to demographics are tracked over time rather than overwritten
* Replace the flat CSV ingestion with a **GCS landing zone** — files would land in a bucket, trigger the DAG, and the ingestion script would read from there instead of local disk
* Add **streaming ingestion** for real-time encounter data using Pub/Sub or Kafka
Parameterize the dbt profiles and config more cleanly using environment variables so the project is easier to run in different environments without editing files

---

## Author

**Ramani Katakam**
