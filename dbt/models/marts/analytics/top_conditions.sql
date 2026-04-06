SELECT
    reason_code,
    reason_description,
    COUNT(*) AS occurrence_count,
    ROUND(SUM(total_claim_cost), 2) AS total_cost
FROM {{ ref('fct_encounters') }}
where reason_description!='Unknown'
GROUP BY reason_code,reason_description
ORDER BY occurrence_count DESC
LIMIT 10