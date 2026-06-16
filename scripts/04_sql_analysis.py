"""
Entain-Style Player Analytics — Script 04: SQL Analysis
=======================================================
Creates SQLite database and runs 8 analytical SQL queries
mirroring real-world sports betting BI work.
"""

import pandas as pd
import sqlite3
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_data.csv')
DB_PATH   = os.path.join(os.path.dirname(__file__), '..', 'data', 'entain_analytics.db')
XL_PATH   = os.path.join(os.path.dirname(__file__), '..', 'data', 'sql_results.xlsx')

QUERIES = {

"Q1_KPI_Executive_Summary": """
-- Q1: Executive KPI Dashboard — single source of truth
SELECT
    COUNT(*)                                           AS TotalPlayers,
    ROUND(SUM(GrossGamingRevenue), 0)                 AS TotalGGR_EUR,
    ROUND(AVG(GrossGamingRevenue), 2)                 AS AvgGGR_per_Player,
    ROUND(AVG(Churned) * 100, 2)                      AS ChurnRate_Pct,
    ROUND(AVG(SessionsPerWeek), 2)                    AS AvgSessionsPerWeek,
    ROUND(AVG(AvgBetSize), 2)                         AS AvgBetSize_EUR,
    SUM(CASE WHEN Device='Mobile App' THEN 1 ELSE 0 END) * 100 / COUNT(*) AS MobileShare_Pct,
    SUM(CASE WHEN BonusUsed=1 THEN 1 ELSE 0 END) * 100 / COUNT(*) AS BonusAdoptionRate_Pct
FROM players
""",

"Q2_Segment_Performance": """
-- Q2: Player segment performance — revenue and churn by segment
SELECT
    PlayerSegment,
    COUNT(*)                                           AS PlayerCount,
    ROUND(SUM(GrossGamingRevenue), 0)                 AS TotalGGR_EUR,
    ROUND(AVG(GrossGamingRevenue), 2)                 AS AvgGGR_EUR,
    ROUND(AVG(Churned) * 100, 2)                      AS ChurnRate_Pct,
    ROUND(AVG(SessionsPerWeek), 2)                    AS AvgSessions,
    ROUND(AVG(AvgBetSize), 2)                         AS AvgBetSize_EUR,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS ShareOfBase_Pct
FROM players
GROUP BY PlayerSegment
ORDER BY TotalGGR_EUR DESC
""",

"Q3_Product_Analysis": """
-- Q3: Product performance and churn by product line
SELECT
    Product,
    COUNT(*)                                           AS Players,
    ROUND(SUM(GrossGamingRevenue), 0)                 AS TotalGGR_EUR,
    ROUND(AVG(GrossGamingRevenue), 2)                 AS AvgGGR_EUR,
    ROUND(AVG(Churned) * 100, 2)                      AS ChurnRate_Pct,
    ROUND(AVG(SessionsPerWeek), 2)                    AS AvgSessions,
    ROUND(AVG(WinRate) * 100, 2)                      AS AvgWinRate_Pct
FROM players
GROUP BY Product
ORDER BY TotalGGR_EUR DESC
""",

"Q4_Country_Revenue": """
-- Q4: Country-level revenue and engagement
SELECT
    Country,
    COUNT(*)                                           AS Players,
    ROUND(SUM(GrossGamingRevenue), 0)                 AS TotalGGR_EUR,
    ROUND(AVG(GrossGamingRevenue), 2)                 AS AvgGGR_EUR,
    ROUND(AVG(Churned) * 100, 2)                      AS ChurnRate_Pct,
    ROUND(AVG(SessionsPerWeek), 2)                    AS AvgSessions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS ShareOfBase_Pct
FROM players
GROUP BY Country
ORDER BY TotalGGR_EUR DESC
""",

"Q5_Device_Engagement": """
-- Q5: Device channel performance
SELECT
    Device,
    COUNT(*)                                           AS Players,
    ROUND(AVG(SessionsPerWeek), 2)                    AS AvgSessionsPerWeek,
    ROUND(AVG(AvgBetSize), 2)                         AS AvgBetSize_EUR,
    ROUND(AVG(GrossGamingRevenue), 2)                 AS AvgGGR_EUR,
    ROUND(AVG(Churned) * 100, 2)                      AS ChurnRate_Pct,
    SUM(CASE WHEN BonusUsed=1 THEN 1 ELSE 0 END) * 100 / COUNT(*) AS BonusRate_Pct
FROM players
GROUP BY Device
ORDER BY AvgGGR_EUR DESC
""",

"Q6_High_Value_Players": """
-- Q6: Top 10% players by GGR — VIP identification
SELECT
    PlayerID,
    Country,
    Product,
    Device,
    PlayerSegment,
    ROUND(GrossGamingRevenue, 2)                      AS GGR_EUR,
    ROUND(SessionsPerWeek, 2)                         AS SessionsPerWeek,
    ROUND(AvgBetSize, 2)                              AS AvgBetSize_EUR,
    DaysSinceLastBet,
    Churned,
    -- Revenue rank using window function
    RANK() OVER (ORDER BY GrossGamingRevenue DESC)    AS RevenueRank,
    -- Running total GGR
    ROUND(SUM(GrossGamingRevenue) OVER
          (ORDER BY GrossGamingRevenue DESC), 0)       AS CumulativeGGR_EUR
FROM players
WHERE GrossGamingRevenue >= (
    SELECT PERCENTILE_SCORE FROM (
        SELECT GrossGamingRevenue,
               PERCENT_RANK() OVER (ORDER BY GrossGamingRevenue) AS PERCENTILE_SCORE
        FROM players
    ) WHERE PERCENTILE_SCORE >= 0.90
    LIMIT 1
)
ORDER BY GrossGamingRevenue DESC
LIMIT 100
""",

"Q7_Churn_Risk_Analysis": """
-- Q7: At-risk player identification for retention campaigns
SELECT
    PlayerID,
    Country,
    Product,
    Device,
    PlayerSegment,
    ROUND(GrossGamingRevenue, 2)                      AS GGR_EUR,
    DaysSinceLastBet,
    ROUND(SessionsPerWeek, 2)                         AS SessionsPerWeek,
    BonusUsed,
    -- Composite risk score
    (
        CASE WHEN DaysSinceLastBet > 30 THEN 3 ELSE 0 END +
        CASE WHEN SessionsPerWeek < 1   THEN 3 ELSE 0 END +
        CASE WHEN WinRate < 0.25        THEN 2 ELSE 0 END +
        CASE WHEN BonusUsed = 0         THEN 1 ELSE 0 END +
        CASE WHEN GrossGamingRevenue > 500 THEN -1 ELSE 0 END
    )                                                  AS RiskScore,
    Churned
FROM players
WHERE PlayerSegment IN ('At Risk', 'Dormant')
    AND Churned = 0
ORDER BY RiskScore DESC, GrossGamingRevenue DESC
LIMIT 200
""",

"Q8_Bonus_Impact": """
-- Q8: Bonus usage impact on engagement and revenue
SELECT
    CASE WHEN BonusUsed=1 THEN 'Bonus Used' ELSE 'No Bonus' END AS BonusGroup,
    COUNT(*)                                           AS Players,
    ROUND(AVG(GrossGamingRevenue), 2)                 AS AvgGGR_EUR,
    ROUND(AVG(SessionsPerWeek), 2)                    AS AvgSessions,
    ROUND(AVG(TotalBets), 1)                          AS AvgTotalBets,
    ROUND(AVG(Churned) * 100, 2)                      AS ChurnRate_Pct,
    ROUND(AVG(DepositCount), 2)                       AS AvgDeposits,
    ROUND(AVG(AvgDeposit), 2)                         AS AvgDepositSize_EUR
FROM players
GROUP BY BonusUsed
""",
}

if __name__ == '__main__':
    print("="*55)
    print("ENTAIN PLAYER ANALYTICS — Script 04: SQL Analysis")
    print("="*55)

    df = pd.read_csv(DATA_PATH)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('players', conn, if_exists='replace', index=False)
    print(f"[DB]    {len(df):,} players loaded into SQLite")

    results = {}
    for name, sql in QUERIES.items():
        try:
            result_df = pd.read_sql_query(sql, conn)
            results[name] = result_df
            print(f"[SQL]   {name}: {len(result_df):,} rows")
        except Exception as e:
            print(f"[WARN]  {name} skipped: {e}")

    conn.close()

    # Export to Excel
    with pd.ExcelWriter(XL_PATH, engine='openpyxl') as writer:
        for sheet_name, result_df in results.items():
            result_df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    print(f"[SAVE]  SQL results -> {XL_PATH}")
    print(f"\nStep 4 complete. All analysis done!\n")

    # Print KPI summary
    if 'Q1_KPI_Executive_Summary' in results:
        kpi = results['Q1_KPI_Executive_Summary'].iloc[0]
        print("EXECUTIVE KPI SNAPSHOT")
        print(f"  Total Players  : {int(kpi['TotalPlayers']):,}")
        print(f"  Total GGR      : EUR {float(kpi['TotalGGR_EUR']):,.0f}")
        print(f"  Churn Rate     : {float(kpi['ChurnRate_Pct']):.1f}%")
        print(f"  Mobile Share   : {float(kpi['MobileShare_Pct']):.1f}%")
        print(f"  Bonus Adoption : {float(kpi['BonusAdoptionRate_Pct']):.1f}%")
