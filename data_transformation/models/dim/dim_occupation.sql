WITH src_occupation as (select * from {{ ref('src_occupation') }})

select 

    {{ dbt_utils.generate_surrogate_key(['id', 'occupation']) }} AS occupation_id,
    occupation,
    occupation_group,
    occupation_field
 from src_occupation

