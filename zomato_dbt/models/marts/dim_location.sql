/*
    dim_location — Location dimension
    One row per unique neighbourhood in Bangalore.
*/

with restaurants as (

    select * from {{ ref('stg_zomato') }}

)

select
    row_number() over (order by location)   as location_id,
    location,
    count(*)                                as restaurant_count,
    round(avg(rate)::numeric, 2)            as avg_rating,
    round(avg(approx_cost)::numeric, 0)     as avg_cost

from restaurants
group by location
order by restaurant_count desc
