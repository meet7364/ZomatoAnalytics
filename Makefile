include .env
export

dbt-run:
	cd zomato_dbt && dbt run

dbt-test:
	cd zomato_dbt && dbt test

dbt-all:
	cd zomato_dbt && dbt run && dbt test