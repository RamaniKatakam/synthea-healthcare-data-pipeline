{{
    config(
        materialized='incremental',
        unique_key='encounter_id',
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

SELECT
    e.encounter_id,
    e.patient_id,
    e.treatment_start_date,
    e.treatment_end_date,
    e.encounter_type,

    -- enrichment
    COALESCE(e.reason_code, c.reason_code,0) AS reason_code,
    COALESCE(e.reason_description,c.reason_description,'Unknown') as reason_description,
    
    -- metrics
    ROUND(e.total_claim_cost, 2) AS total_claim_cost,
    ROUND(e.insurance_coverage, 2) AS insurance_coverage
FROM {{ ref('stg_encounters') }} e
LEFT JOIN {{ ref('int_conditions_per_encounter') }} c
    ON e.encounter_id = c.encounter_id

{% if is_incremental() %}
    where e.treatment_start_date > (select COALESCE(MAX(treatment_start_date),'1900-01-01') FROM {{ this }})
{% endif %}