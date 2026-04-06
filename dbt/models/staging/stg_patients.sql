select id as patient_id, first as first_name, last as last_name, COALESCE(gender, 'Unknown') AS gender, DATE(birthdate) as birth_date, DATE(deathdate) as death_date,
safe_cast(HEALTHCARE_EXPENSES as numeric) as healthcare_expenses,
safe_cast(HEALTHCARE_COVERAGE as numeric) as healthcare_coverage
from{{ source('raw','patients') }}