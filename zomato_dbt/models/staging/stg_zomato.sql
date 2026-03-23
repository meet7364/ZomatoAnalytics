/*
    stg_zomato — Staging model
    Single source of truth for all downstream mart models.
    Casts types, filters out null ratings.
*/

with source as (

    select * from {{ source('raw', 'zomato') }}

),

cleaned as (

    select
        name,
        location,
        restaurant_type,
        cuisines,

        rate::float                     as rate,
        votes::int                      as votes,
        approx_cost::int                as approx_cost,
        online_order::boolean           as online_order,
        book_table::boolean             as book_table,

        listed_type,
        listed_city

    from source
    where rate is not null

)

select * from cleaned
