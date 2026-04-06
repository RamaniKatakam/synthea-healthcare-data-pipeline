
select reason_code,reason_description from {{ ref("stg_conditions")}}