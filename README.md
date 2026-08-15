# Zomato Bangalore Analytics Dashboard

A full-stack data analytics project analyzing **51,696 restaurants** across **93 locations** in Bangalore using the Zomato dataset. Covers end-to-end data engineering — ingestion, cleaning, transformation via dbt, EDA with Pandas, and an interactive Streamlit dashboard.

> 🔗 **Live Dashboard:** [zomato-analytics-dashboard-meet7364.streamlit.app](https://zomato-analytics-dashboard-meet7364.streamlit.app/)

---

## 📊 Dashboard Features

The interactive dashboard is built with **Streamlit + Plotly** and includes:

| Section | What it shows |
|---|---|
| **KPI Row** | Total restaurants, locations, avg rating, median cost, total votes |
| **Location Insights** | Top N locations by count & avg rating (interactive, adjustable slider) |
| **Ratings & Cost Distribution** | Histograms for rating spread and cost distribution (up to ₹3,000) |
| **Order & Booking Behaviour** | Online vs offline avg rating by restaurant type; table booking impact |
| **Cuisines & Restaurant Types** | Top cuisines by avg rating; restaurant type breakdown (donut/bar toggle) |
| **Deep Dives** | Cost vs rating scatter + OLS trendline; votes vs rating scatter |

**Cross-filtering:** Click any bar or pie slice to filter all charts simultaneously. Use the sidebar to filter by location, restaurant type, online order, cost range, and minimum rating.

---

## 📁 Project Structure

```
ZomatoBangalore/
├── dashboards/
│   └── dashboard_preview.png       # Static dashboard preview
├── data/
│   ├── processed/
│   │   └── zomato_clean.csv        # Cleaned dataset (output of clean.py)
│   └── raw/
│       └── zomato.csv              # Raw Kaggle dataset
├── notebooks/
│   └── eda.ipynb                   # Exploratory data analysis
├── plots/                          # All generated visualizations
│   ├── avg_rating_by_location.jpg
│   ├── avg_rating_by_type.jpg
│   ├── cost_distribution.jpg
│   ├── cost_vs_no_booking.jpg
│   ├── online_vs_offline_rating.jpg
│   ├── restaurant_type_breakdown.jpg
│   ├── restaurant_count.jpg
│   ├── top_cuisines_rating.jpg
│   ├── top_location_count.jpg
│   └── votes_rating.jpg
├── src/
│   ├── __init__.py
│   ├── clean.py                    # Data cleaning pipeline
│   └── load.py                     # Data loading utilities
├── zomato_dbt/                     # dbt transformation layer
│   ├── dbt_project.yml
│   └── models/
│       ├── marts/
│       │     ├── dim_cuisine.sql
│       │     ├── dim_location.sql
│       │     ├── dim_restaurant_type.sql
│       │     └── fct_restaurants.sql
│       └── staging/
│           ├── schema.yml
│           ├── sources.yml
│           └── stg_zomato.sql
├── streamlit_app.py                # Interactive analytics dashboard
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🔧 Tech Stack

| Layer | Tool |
|---|---|
| Data Source | Kaggle — Zomato Bangalore Dataset |
| Data Cleaning | Python · Pandas |
| Transformation | dbt (Data Build Tool) |
| Exploration | Jupyter Notebook |
| Dashboard | Streamlit · Plotly |
| Package Management | uv / pyproject.toml |

---

## 🚀 Getting Started (Run Locally)

### 1. Clone the repository

```bash
git clone https://github.com/meet7364/ZomatoAnalytics.git
cd ZomatoBangalore
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Add the raw dataset

Download [`zomato.csv`](https://www.kaggle.com/datasets/himanshupoddar/zomato-bangalore-restaurants) from Kaggle and place it at:

```
data/raw/zomato.csv
```

### 4. Run data cleaning

```bash
uv run python src/clean.py
```

This reads `data/raw/zomato.csv`, cleans it, and outputs `data/processed/zomato_clean.csv`.

### 5. (Optional) Run dbt transformations

```bash
make dbt-all
```

### 6. Launch the dashboard

```bash
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧹 Data Cleaning Steps

The raw Zomato dataset required significant cleaning before analysis:

- Extracted numeric rating from strings like `"4.1/5"` → `4.1`
- Removed commas from cost values like `"1,200"` → `1200`
- Dropped rows with `"NEW"` or `"-"` as rating values
- Handled null values in `approx_cost`, `cuisines`, and `location`
- Standardised `online_order` and `book_table` to `Yes` / `No` values

---

## 🏗️ dbt Models

### Staging
- `stg_zomato.sql` — base cleaning and type casting from raw source

### Marts
- `dim_location.sql` — unique locations dimension
- `dim_cuisine.sql` — unique cuisines dimension
- `dim_restaurant_type.sql` — restaurant type dimension
- `fct_restaurants.sql` — fact table joining all dimensions with ratings, cost, votes

### Tests
- Not-null checks on key fields
- Unique constraints on dimension primary keys
- Accepted value ranges for ratings

---

## 📈 Key Insights

*(Rerun 2026-08-15: `src/clean.py` regenerated `data/processed/zomato_clean.csv` byte-identical to the committed version — 51,696 rows, 93 locations. `notebooks/eda.ipynb` executed end-to-end; two numbers below were corrected against the real output.)*

- **BTM** has the highest restaurant count (~5,000+) across all 93 Bangalore locations
- **Lavelle Road** tops the avg rating chart among areas with 30+ restaurants (~4.1)
- Restaurants that accept **online orders** have a slightly higher avg rating vs offline
- **Table booking** restaurants average significantly higher ratings (**4.14 vs 3.62**)
- **Modern Indian** has the highest avg rating (4.31) among cuisines with 50+ listings
- Most restaurants cluster between ratings **3.5 – 4.0**, with median cost around **₹400**
- Higher cost restaurants show a positive OLS trendline with rating (cost vs rating scatter)
- **Quick Bites** (37.2%) and **Casual Dining** (20.1%) dominate restaurant types

---

## 📦 Dataset

- **Source:** [Zomato Bangalore Restaurants — Kaggle](https://www.kaggle.com/datasets/himanshupoddar/zomato-bangalore-restaurants)
- **Size:** 51,696 restaurant records · 93 locations
- **Fields:** `name`, `location`, `cuisines`, `approx_cost`, `rate`, `votes`, `online_order`, `book_table`, `rest_type`, `listed_type`

---

## 🙌 Acknowledgements

- Dataset by Kaggle community contributors
- [dbt](https://www.getdbt.com/) for making SQL transformations modular and testable
- [Streamlit](https://streamlit.io/) & [Plotly](https://plotly.com/) for the interactive dashboard

---

## Author

**Meet Modi** — B.Tech CSE (Data Science), VIT Chennai  
[LinkedIn](https://www.linkedin.com/in/meet-modi-bb57752b8/) · [GitHub](https://github.com/meet7364)