# 🛒 Walmart Business Insights Dashboard
### Power BI-Style Analytics — Built in Python

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=flat&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7%2B-11557C?style=flat)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat&logo=jupyter&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 📌 Project Overview

This project replicates a **Power BI business intelligence dashboard** entirely in Python using real Walmart store sales data.
It analyzes **45 stores**, **6,435 weekly observations**, and **$6.74 billion** in total revenue across 2010–2012 — producing 5 publication-quality dashboard charts covering every angle of retail performance analytics.

> 🎯 **Purpose:** Demonstrate end-to-end data analytics skills — data ingestion, feature engineering, statistical analysis, and professional dashboard visualization — using only Python's open-source stack.

---

## 📊 Dashboard Previews

### Chart 1 — KPI Overview & Monthly Revenue Trend
![Overview](images/01_overview_dashboard.png)

### Chart 2 — Store Performance Analysis
![Store Performance](images/02_store_performance.png)

### Chart 3 — Economic Factors Correlation
![Economic Factors](images/03_economic_factors.png)

### Chart 4 — Holiday & Seasonal Patterns
![Holiday Seasonal](images/04_holiday_seasonal.png)

### Chart 5 — Advanced Analytics & Volatility
![Advanced Analytics](images/05_advanced_analytics.png)

---

## 📁 Repository Structure

```
walmart-dashboard/
│
├── 📓 walmart_analysis.ipynb     ← Main Jupyter Notebook (run this)
├── 🐍 walmart_dashboard.py       ← Python module with all chart functions
│
├── 📂 data/
│   └── Walmart.csv               ← Raw dataset (6,435 records)
│
├── 📂 images/                    ← Generated chart outputs
│   ├── 01_overview_dashboard.png
│   ├── 02_store_performance.png
│   ├── 03_economic_factors.png
│   ├── 04_holiday_seasonal.png
│   └── 05_advanced_analytics.png
│
├── 📋 requirements.txt           ← Python dependencies
└── 📄 README.md                  ← This file
```

---

## 🗂️ Dataset

| Column | Description |
|--------|-------------|
| `Store` | Store number (1–45) |
| `Date` | Week start date |
| `Weekly_Sales` | Sales for the given store in that week ($) |
| `Holiday_Flag` | 1 = Holiday week, 0 = Regular week |
| `Temperature` | Regional temperature (°F) |
| `Fuel_Price` | Cost of fuel in the region ($/gallon) |
| `CPI` | Consumer Price Index |
| `Unemployment` | Regional unemployment rate (%) |

**Source:** [Walmart Recruiting — Store Sales Forecasting (Kaggle)](https://www.kaggle.com/datasets/yasserh/walmart-dataset)

---

## 📈 Dashboard Modules

### 1️⃣ KPI Overview Dashboard
- **$6.74B** total network revenue
- **$1.05M** average weekly sales per store
- **$3.82M** peak single-week record
- **$505M** holiday week revenue (7.5% of total)
- Monthly revenue trend with year-over-year comparison
- Annual and quarterly breakdowns

### 2️⃣ Store Performance Analysis
- All 45 stores ranked by cumulative 3-year revenue
- Scatter plot: average weekly sales vs variability (CV)
- Box plots for top 10 stores — distribution & outliers
- Full performance scorecard table (revenue, share, growth)

### 3️⃣ Economic Factors Correlation
- Scatter plots: Unemployment / Fuel Price / Temperature vs Sales
- Band analysis (bucketed economic conditions vs avg sales)
- **Full correlation matrix heatmap** for all 5 variables
- Trend lines with Pearson r coefficients

### 4️⃣ Holiday & Seasonal Analysis
- Side-by-side holiday vs regular week comparison (top 20 stores)
- Holiday sales lift quantification
- Seasonal monthly average pattern (12-month cycle)
- Week-of-year heatmap with holiday markers

### 5️⃣ Advanced Analytics
- Network-wide rolling averages (4-week and 13-week)
- Sales volatility overlay (standard deviation bands)
- Store × month performance heatmap (Top 15 stores)
- Store tier analysis by revenue percentile

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Option A — Run Python Script
```bash
python walmart_dashboard.py
```
Generates all 5 chart images in `./images/`

### Option B — Jupyter Notebook (Recommended)
```bash
jupyter notebook walmart_analysis.ipynb
```
Run all cells to see the full interactive analysis with insights.

---

## 🔧 Requirements

```
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
jupyter>=1.0.0
notebook>=6.5.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 💡 Key Findings

| Insight | Result |
|---------|--------|
| 🏆 Top Store | **Store #20** — $301.4M over 3 years |
| 📅 Peak Month | **December** (Holiday Season lift) |
| 🎉 Holiday Sales Lift | **+7.5%** vs regular weeks |
| 📉 Unemployment Impact | Weak negative correlation (r ≈ −0.10) |
| ⛽ Fuel Price Impact | Very weak correlation (r ≈ −0.01) |
| 📈 Best Year | **2011** — $2.45B total network revenue |
| 🔁 Seasonality | Strong Q4 spike, stable Q1–Q3 |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.8+** | Core language |
| **Pandas** | Data loading, cleaning, feature engineering |
| **NumPy** | Statistical calculations, array ops |
| **Matplotlib** | All chart rendering & dashboard layout |
| **Jupyter** | Interactive notebook interface |

---

## 👤 Author

Built as a portfolio project demonstrating **Power BI-equivalent analytics in Python**.

- 📧 Feel free to fork, star ⭐, and adapt for your own retail datasets
- 🔗 Dataset: [Kaggle — Walmart Store Sales](https://www.kaggle.com/datasets/yasserh/walmart-dataset)

---

*Built with Python · matplotlib · pandas · Real Walmart Data*
