
            {{ config(materialized='ephemeral') }}
            SELECT 1 AS colname
            