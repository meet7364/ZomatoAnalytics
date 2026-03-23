/*
    dim_cuisine — Cuisine dimension
    Explodes the comma-separated cuisines column so each row
    represents one cuisine for one restaurant.
    Then aggregates to one row per unique cuisine.
*/

with restaurants as (

    select * from {{ ref('stg_zomato') }}

),

exploded as (

    select
        name,
        rate,
        trim(unnest(string_to_array(cuisines, ','))) as cuisine

    from restaurants
    where cuisines is not null

)

select
    cuisine,
    count(*)                            as restaurant_count,
    round(avg(rate)::numeric, 2)        as avg_rating

from exploded
group by cuisine
order by restaurant_count desc
