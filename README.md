# Player Analytics & Churn Intelligence Platform
### Sports Betting Analytics Portfolio Project

---

## Business Problem

A sports betting operator with 10,000 active players across 6 European markets needed answers to three critical questions:

- **Who are our most valuable players** — and who is about to churn?
- **Which products and channels** drive the highest engagement and revenue?
- **Do retention bonus campaigns actually work** — and how do we measure it?

This project delivers a complete analytical platform answering all three.

---

## Key Findings

| Metric | Result |
|---|---|
| Total Players Analysed | 10,000 |
| Total Gross Gaming Revenue | EUR 8,003,232 |
| Overall Churn Rate | 8.9% |
| Mobile App Share | 57.5% |
| Best Churn Predictor | Days Since Last Bet |
| Best ML Model | Gradient Boosting (AUC: 0.708) |
| A/B Test CTR Uplift | +63% (statistically significant, p<0.0001) |
| Critical Risk Players | 72 players flagged for immediate intervention |

---

## Business Recommendations

**R1 — Reactivation Campaign (HIGH PRIORITY)**
288 players flagged as Critical or High Risk with prior GGR > EUR 200. Target with personalised bonus offers within 7 days of last bet. Expected CTR uplift: +63% based on A/B test results.

**R2 — Mobile-First Strategy**
57.5% of players use Mobile App and show lower churn rates than Web users. Prioritise mobile UX improvements and mobile-exclusive promotions.

**R3 — Sports Betting Retention**
Sports Betting has the lowest churn rate of all products. Cross-sell Sports Betting to Casino and Poker players showing early churn signals.

**R4 — Bonus Programme Expansion**
Bonus-using players show significantly higher GGR and lower churn. Increasing bonus adoption from 61% to 75% is projected to meaningfully reduce overall churn rate.

---

## Project Architecture

```
player-analytics/
│
├── data/
│   ├── player_data.csv          # 10,000 player records (17 features)
│   ├── player_with_risk.csv     # + Churn probability & risk category
│   ├── powerbi_ready.csv        # Flat export optimised for Power BI
│   ├── entain_analytics.db      # SQLite database for SQL analysis
│   ├── sql_results.xlsx         # 8 SQL query results (one sheet each)
│   └── model_metrics.json       # ML model evaluation results
│
├── scripts/
│   ├── 01_eda.py                # EDA, KPI summary, segmentation charts
│   ├── 02_churn_model.py        # ML models, ROC curves, risk scoring
│   ├── 03_ab_test.py            # A/B test simulation and analysis
│   └── 04_sql_analysis.py       # SQLite DB + 8 analytical SQL queries
│
├── screenshots/                 # 6 chart outputs for dashboard/README
└── README.md
```

---

## SQL Queries (8 total)

| Query | Business Question |
|---|---|
| Q1 — Executive KPI Summary | Single source of truth for leadership |
| Q2 — Segment Performance | Revenue and churn by player segment |
| Q3 — Product Analysis | Which products drive highest GGR and retention? |
| Q4 — Country Revenue | Geographic performance breakdown |
| Q5 — Device Engagement | Mobile vs Web vs Tablet behaviour |
| Q6 — High Value Players | VIP identification with window functions |
| Q7 — Churn Risk Scoring | At-risk players for retention campaigns |
| Q8 — Bonus Impact | Does bonus usage improve engagement? |

---

## ML Model Results

| Model | AUC | CV AUC | Accuracy |
|---|---|---|---|
| Logistic Regression | 0.675 | 0.673 | 91.1% |
| Random Forest | 0.706 | 0.701 | 91.3% |
| **Gradient Boosting** | **0.708** | **0.724** | **90.6%** |

Top churn predictors: Days Since Last Bet, Sessions Per Week, Win Rate, Average Bet Size

---

## A/B Test Results — Retention Bonus Campaign

| Metric | Control | Treatment | Uplift | Significance |
|---|---|---|---|---|
| Sample Size | 4,449 | 4,370 | — | — |
| CTR | 17.5% | 28.5% | +63.0% | p < 0.0001 |
| Conversion Rate | 11.7% | 18.5% | +58.3% | p < 0.0001 |
| Revenue per Player | EUR 10.51 | EUR 17.66 | +68.0% | — |

---

## How to Run

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/player-analytics.git
cd player-analytics

# Install dependencies
pip install pandas numpy matplotlib seaborn scikit-learn plotly scipy openpyxl

# Run the full pipeline
python scripts/01_eda.py          # EDA and segmentation charts
python scripts/02_churn_model.py  # ML churn prediction
python scripts/03_ab_test.py      # A/B test analysis
python scripts/04_sql_analysis.py # SQL queries and Excel export

# Open data/powerbi_ready.csv in Power BI Desktop for dashboard
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python / Pandas | Data generation, cleaning, feature engineering |
| Scikit-learn | Logistic Regression, Random Forest, Gradient Boosting |
| SciPy | Statistical significance testing (chi-squared) |
| Matplotlib / Seaborn | EDA charts and model visualisation |
| SQLite / SQL | Star schema database and 8 analytical queries |
| Power BI | Executive KPI dashboard (powerbi_ready.csv) |
| openpyxl | Multi-sheet Excel export of SQL results |

---

## Author

**Sowmiyaraksha Naik** — Data Analyst | Python · SQL · Power BI | Brussels, Belgium

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/sowmiyaraksha-naik-780511305)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/jobsnaik23)
