# 🏥 Healthcare Data Engineering Pipeline (Synthea + BigQuery + dbt)

## 📌 Project Overview

This project demonstrates an **end-to-end healthcare data engineering pipeline** built using modern data stack tools. It simulates real-world Electronic Health Records (EHR) processing using synthetic patient data.

The pipeline ingests raw healthcare data, transforms it into a structured analytical model and enables insights into **patient encounters, treatment costs, and disease trends**.

---

## 🎯 Business Objective

Healthcare organizations need reliable pipelines to:

* Track patient encounters and treatments
* Analyze healthcare costs and insurance coverage
* Identify high-risk patients and common conditions

This project models these use cases by transforming raw data into **analytics-ready datasets**.

---

## 📂 Data

**Dataset:** Synthetic Healthcare Data (Synthea)

- Source: [https://synthetichealth.github.io/synthea/](https://synthetichealth.github.io/synthea/)  
- Purpose: Simulate realistic healthcare data for analytics while preserving privacy

---

## 📌 Architecture Overview

The pipeline follows a modern ELT approach:

- Raw CSV data is ingested into BigQuery
- dbt is used for transformations (staging → intermediate → marts)
- Analytics-ready tables are built for reporting

### 🔄 Orchestration Layer (Apache Airflow)

The pipeline is orchestrated using Apache Airflow (running in Docker), which manages task dependencies and execution flow.

- DAG: `healthcare_pipeline`
- Execution flow:
```
Ingest Data → dbt run → dbt test
```
- Handles scheduling, retries, and monitoring
- Ensures transformations run only after successful ingestion

---

## 🧰 Tech Stack

* **Cloud Data Warehouse:** BigQuery
* **Transformation Layer:** dbt
* **Ingestion:** Python
* **Data Modeling:** Star Schema
* **Orchestration:** Apache Airflow (Dockerized)

---

## 🔄 Airflow Pipeline

The project uses Airflow to automate the end-to-end workflow.

### DAG: `healthcare_pipeline`

#### Tasks:

1. **Ingest Data**
 - Runs:
   ```
   python /opt/project/scripts/upload_to_bigquery.py
   ```
 - Loads CSV data into BigQuery
 - Uses `WRITE_TRUNCATE` for full refresh

2. **Run dbt Models**
 - Executes:
   ```
   dbt run --profiles-dir /opt/project/dbt/profiles
   ```
 - Builds staging, intermediate, and mart models

3. **Run dbt Tests**

---

## 🏗️ Architecture

![Architecture Diagram](docs/architecture.png)

---

## 🧱 Data Model (Star Schema)

### Core Tables:

* **Fact Table**

  * `fct_encounters` → patient encounters, costs, treatments

* **Dimensions**

  * `dim_patient` → patient demographics + financial summary
  * `dim_condition` → medical conditions

```
                     dim_patient
                      |
                      |
dim_condition —— fct_encounters
```
---

## 🔄 Data Lineage (dbt DAG)

[Lineage Graphs](https://github.com/RamaniKatakam/synthea-healthcare-data-pipeline/tree/main/docs/lineage)

This project includes dbt lineage graphs to illustrate model dependencies and transformation flow.

---

## 🔄 Data Pipeline Layers

### 🟢 Staging (`stg_*`)

* Cleans and standardizes raw data
* Minimal transformations

### 🟡 Intermediate (`int_*`)

* Handles data aggregation and deduplication
* Example: condition enrichment per encounter

### 🔵 Marts (`dim_*`, `fct_*`)

* Business-ready models
* Star schema implementation

---

## ⚙️ Key Features

* ✅ Built using **modular dbt models (`ref`, `source`)**
* ✅ Implemented **incremental loading** for fact table
* ✅ Handled **missing data using enrichment logic (COALESCE)**
* ✅ Created **healthcare-specific transformations (age using death date)**
* ✅ Designed **clean star schema for analytics**

---

## 📊 Analytical Models

Located in:
`dbt/models/marts/analytics/`

### 1️⃣ Patient Summary

* Total visits per patient
* Total & average healthcare costs

### 2️⃣ Condition Analysis

* Most common conditions
* Total cost per condition

---

## 🔍 Sample Insights

* 📈 Identify **high-cost patients**
* 🏥 Analyze **most frequent medical conditions**
* 💰 Track **total healthcare spending trends**

---

## 🧪 Data Quality

* Implemented **dbt tests**:

  * `not_null`
  * `unique`
* Ensured **consistent joins and grain alignment**
* Validated data using reconciliation logic

---

## 🚀 How to Run the Project

### Run Airflow (Docker)

```bash
docker-compose up

Airflow UI: http://localhost:8080
Username: admin
Password: admin

Trigger DAG: healthcare_pipeline
```

---

## 📁 Project Structure

```
├── data/                     # Raw datasets (Not published to Git)
├── dags/                     # Airflow DAGs
├── scripts/                  # Ingestion scripts
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   ├── marts/
│   │   │   ├── core/
│   │   │   └── analytics/
├── docs/                     # Architecture & data model diagrams
├── dashboards/               # visualization screenshots
└── README.md
```

---

## 🧠 Key Design Decisions

* Used **Synthea dataset** to simulate real-world healthcare data without privacy constraints
* Modeled **encounters as fact table** and **patients/conditions as dimensions**
* Applied **incremental loading only to fact table** (industry best practice)
* Avoided over-engineering by keeping dimensions simple and reusable

---

## 📈 Future Improvements

* Implement Slowly Changing Dimensions (SCD Type 2)
* Add streaming ingestion (Kafka)

---

## 💬 About This Project

This project was built to demonstrate **production-style data engineering practices**, including:

* Built end-to-end ELT pipeline using dbt and BigQuery
* Designed star schema (dim + fact tables)
* Implemented data quality checks using dbt tests
* Orchestrated pipeline using Apache Airflow running in Docker

---

## 👩‍💻 Author

**Ramani Katakam**

---

## ⭐ If you found this useful

Consider giving the repo a star ⭐
