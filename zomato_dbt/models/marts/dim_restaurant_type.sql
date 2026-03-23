/*
    dim_restaurant_type — Restaurant type dimension
    One row per unique restaurant type with aggregates.
*/

with restaurants as (

    select * from {{ ref('stg_zomato') }}

)

select
    restaurant_type,
    count(*)                                as restaurant_count,
    round(avg(rate)::numeric, 2)            as avg_rating,
    round(avg(approx_cost)::numeric, 0)     as avg_cost

from restaurants
where restaurant_type is not null
group by restaurant_type
order by restaurant_count desc
