SELECT *
FROM {{ source('pg_catalog', 'pg_tables') }}
limit 1
