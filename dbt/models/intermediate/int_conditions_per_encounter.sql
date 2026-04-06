select encounter_id,any_value(reason_code) as reason_code,any_value(reason_description) as reason_description
from {{ ref("stg_conditions")}}
group by encounter_id