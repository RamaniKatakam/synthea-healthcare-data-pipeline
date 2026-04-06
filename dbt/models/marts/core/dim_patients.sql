select patient_id, first_name, last_name, coalesce(trim(coalesce(NULLIF(first_name,''),'') || ' ' || coalesce(NULLIF(last_name,''),'')),'Unknown') as patient_name, gender, birth_date, DATE_DIFF(coalesce(date(death_date),CURRENT_DATE()),date(birth_date),Year) as patient_age, 
case 
 when death_date is not null and death_date<=CURRENT_DATE() then 'Alive'
 else 'Not Alive'
end as patient_vitals_status,
round(healthcare_expenses,2) as healthcare_expenses,
round(healthcare_coverage,2) as healthcare_coverage
from {{ ref("stg_patients") }}