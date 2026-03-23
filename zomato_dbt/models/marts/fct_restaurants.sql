/*
    fct_restaurants — Fact table
    One row per restaurant. This is the primary table
    that Tableau connects to for the dashboard.
*/

with stg as (

    select * from {{ ref('stg_zomato') }}

)

select
    name,
    location,
    restaurant_type,
    rate,
    votes,
    approx_cost,
    online_order,
    book_table,
    listed_type,
    cuisines

from stg
