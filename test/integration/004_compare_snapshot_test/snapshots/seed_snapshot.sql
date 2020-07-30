{% snapshot seed_snapshot %}

    {{
        config(
          unique_key="'id' || '-' || 'first_name'",
          strategy='timestamp',
          updated_at='updated_at'
        )
    }}

    select * from {{ ref('seed') }}

{% endsnapshot %}