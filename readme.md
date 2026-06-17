# ⚽ Football Team Performance Dashboard

Interactive football analytics dashboard built with Streamlit and Snowflake.

The application visualizes analytical models produced by the **football-analytics-pipeline** project and provides an intuitive way to explore football team performance and current form trends.

---

## 🚀 Features

### 📋 Recent Matches Form

Displays:

* last 10 matches
* match scores and results
* visual form indicators (W / D / L)

### 📈 Rolling Average Goals

Interactive chart showing:

* average goals scored over the previous 5 matches
* average goals conceded over the previous 5 matches

This allows users to quickly identify attacking and defensive trends.

### ⚡ Current Streak Tracking

Displays:

* current streak type (WIN / DRAW / LOSS)
* streak length
* detailed breakdown of matches within the streak

### 🌙 Modern Responsive UI

Custom dark theme built with Streamlit and Plotly, optimized for desktop and mobile viewing.

---

## 🛠️ Tech Stack

### Frontend

* Streamlit
* Plotly

### Data Processing

* Pandas

### Data Warehouse

* Snowflake

### Data Transformation

* dbt

### Language

* Python

---

## 🏗️ Architecture

```text
 football-pipeline
        ↓
    Snowflake
        ↓
Streamlit Dashboard
```

The dashboard itself does not perform any ETL or transformations.

It consumes analytical models created in the separate repository:

**football-pipeline**

---

## 📊 Data Sources

Main analytical tables consumed by the application:

* `FCT_TEAM_ROLLING_FORM_LAST_5`
* `FCT_MATCHES`

---

## ⚡ Performance

The application uses Streamlit caching to:

* reuse Snowflake connections
* reduce query execution time
* minimize Snowflake compute usage

---

## 💻 Local Setup

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure secrets

Create:

```text
.streamlit/secrets.toml
```

Example:

```toml
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE="FOOTBALL_DB"
SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
```

---

## ▶️ Run the Dashboard

```bash
streamlit run app.py
```

---

## 📦 Related Project

This dashboard is powered by data generated in:

**football-pipeline**

The pipeline is responsible for:

* ingesting football data from external APIs,
* loading raw data into Snowflake,
* transforming data using dbt,
* producing analytical Gold models consumed by this dashboard.
