# Synthea Healthcare Data Pipeline

## Overview

This project builds an end-to-end data engineering pipeline using synthetic Electronic Health Record (EHR) data. The pipeline ingests raw healthcare data, transforms it into a structured data warehouse model and enables analytical insights on patient encounters and medical conditions.

---

## Tech Stack

* Google BigQuery
* dbt (data transformations)
* Python (data ingestion)
* SQL
* (Planned) Apache Airflow
* (Planned) Kafka

---

## Dataset

Synthetic healthcare dataset generated using Synthea, including:

* Patients
* Encounters (hospital visits)
* Conditions (diagnoses)

---

## Architecture

CSV Files → Python Ingestion → BigQuery (Raw) → dbt Models (Staging → Marts) → Analytics

---

## Data Model

### Staging Layer

* stg_patients
* stg_encounters
* stg_conditions

### Mart Layer

* dim_patient
* dim_condition
* fact_encounters
  
---

## Pipeline Steps

1. Load raw CSV into BigQuery
2. Build staging models in dbt
3. Transform into star schema
4. Run analytical queries

---

## Sample Insights

* Patient visit frequency
* Most common medical conditions
* Encounters by age group

---

## Future Improvements

* Add Apache Airflow for orchestration
* Add Kafka for real-time streaming
* Implement data quality monitoring
* Add dashboard (Power BI)

---

## Screenshots



---

## Author
Ramani Katakam
