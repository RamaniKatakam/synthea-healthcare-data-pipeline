select patient as patient_id, encounter as encounter_id, safe_cast(code as int64) as reason_code, description as reason_description
from{{ source('raw','conditions') }}