select
    p.patient_id,
    p.patient_name,
    p.patient_age,
    p.gender,
    p.patient_vitals_status,
    count(f.encounter_id) as total_visits,
    round(sum(f.total_claim_cost), 2) as total_spent,
    round(avg(f.total_claim_cost), 2) as avg_visit_cost
from {{ ref("fct_encounters") }} f
join {{ ref("dim_patients") }} p on f.patient_id = p.patient_id
group by p.patient_id, p.patient_name,p.patient_age, p.patient_vitals_status, p.gender
