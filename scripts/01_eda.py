"""
Entain-Style Player Analytics — Script 01: Exploratory Data Analysis
=====================================================================
Analyses 10,000 player records across product, device, country,
engagement, and churn dimensions. Generates charts for dashboard.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

DATA_PATH    = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_data.csv')
CHARTS_DIR   = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
os.makedirs(CHARTS_DIR, exist_ok=True)

PALETTE = {'Champions':'#1D9E75','Loyal Players':'#3B82F6','At Risk':'#F59E0B','Dormant':'#6B7280','Lost':'#EF4444'}
sns.set_theme(style='whitegrid')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})

def load():
    df = pd.read_csv(DATA_PATH)
    print(f"[LOAD]  {len(df):,} players loaded")
    return df

def kpi_summary(df):
    print("\n" + "="*55)
    print("EXECUTIVE KPI SUMMARY")
    print("="*55)
    print(f"Total Players          : {len(df):,}")
    print(f"Total GGR              : EUR {df['GrossGamingRevenue'].sum():,.0f}")
    print(f"Avg GGR per Player     : EUR {df['GrossGamingRevenue'].mean():,.2f}")
    print(f"Overall Churn Rate     : {df['Churned'].mean():.1%}")
    print(f"Avg Sessions/Week      : {df['SessionsPerWeek'].mean():.2f}")
    print(f"Avg Bet Size           : EUR {df['AvgBetSize'].mean():,.2f}")
    print(f"Mobile App Share       : {(df['Device']=='Mobile App').mean():.1%}")
    print(f"Top Product            : {df['Product'].value_counts().index[0]}")
    print("="*55)

def plot_segment_overview(df):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Player Segmentation Overview', fontsize=14, fontweight='bold', y=1.02)

    seg_order = ['Champions','Loyal Players','At Risk','Dormant','Lost']
    colors = [PALETTE[s] for s in seg_order]

    # Count
    counts = df['PlayerSegment'].value_counts().reindex(seg_order)
    axes[0].barh(seg_order, counts.values, color=colors, edgecolor='white')
    for i, v in enumerate(counts.values):
        axes[0].text(v+20, i, f'{v:,}', va='center', fontsize=9)
    axes[0].set_title('Player Count by Segment', fontweight='bold')
    axes[0].set_xlabel('Number of Players')

    # GGR
    ggr = df.groupby('PlayerSegment')['GrossGamingRevenue'].sum().reindex(seg_order)
    axes[1].barh(seg_order, ggr.values/1000, color=colors, edgecolor='white')
    for i, v in enumerate(ggr.values):
        axes[1].text(v/1000+5, i, f'EUR {v/1000:.0f}K', va='center', fontsize=9)
    axes[1].set_title('GGR by Segment (EUR K)', fontweight='bold')
    axes[1].set_xlabel('Gross Gaming Revenue (K)')

    # Churn rate
    churn = df.groupby('PlayerSegment')['Churned'].mean().reindex(seg_order) * 100
    bars = axes[2].barh(seg_order, churn.values, color=colors, edgecolor='white')
    for i, v in enumerate(churn.values):
        axes[2].text(v+0.3, i, f'{v:.1f}%', va='center', fontsize=9)
    axes[2].set_title('Churn Rate by Segment', fontweight='bold')
    axes[2].set_xlabel('Churn Rate (%)')
    axes[2].axvline(df['Churned'].mean()*100, color='red', linestyle='--', alpha=0.5, label='Overall avg')
    axes[2].legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/01_segment_overview.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("[CHART] 01_segment_overview.png")

def plot_churn_drivers(df):
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle('Key Churn Drivers', fontsize=14, fontweight='bold')

    # Sessions vs churn
    df['SessionBand'] = pd.cut(df['SessionsPerWeek'], bins=[0,1,3,7,15,25],
        labels=['<1','1-3','3-7','7-15','15+'])
    churn_sess = df.groupby('SessionBand', observed=True)['Churned'].mean()*100
    axes[0,0].bar(churn_sess.index, churn_sess.values,
        color=['#EF4444' if v>15 else '#1D9E75' for v in churn_sess.values], edgecolor='white')
    for i, v in enumerate(churn_sess.values):
        axes[0,0].text(i, v+0.3, f'{v:.1f}%', ha='center', fontsize=9, fontweight='bold')
    axes[0,0].set_title('Churn Rate by Sessions per Week', fontweight='bold')
    axes[0,0].set_xlabel('Sessions / Week')
    axes[0,0].set_ylabel('Churn Rate (%)')

    # Days inactive vs churn
    df['InactiveBand'] = pd.cut(df['DaysSinceLastBet'], bins=[-1,7,14,30,60,180],
        labels=['0-7d','8-14d','15-30d','31-60d','60d+'])
    churn_inact = df.groupby('InactiveBand', observed=True)['Churned'].mean()*100
    axes[0,1].bar(churn_inact.index, churn_inact.values,
        color=['#EF4444' if v>15 else '#1D9E75' for v in churn_inact.values], edgecolor='white')
    for i, v in enumerate(churn_inact.values):
        axes[0,1].text(i, v+0.3, f'{v:.1f}%', ha='center', fontsize=9, fontweight='bold')
    axes[0,1].set_title('Churn Rate by Days Since Last Bet', fontweight='bold')
    axes[0,1].set_xlabel('Days Since Last Bet')
    axes[0,1].set_ylabel('Churn Rate (%)')

    # Product vs churn
    prod_churn = df.groupby('Product')['Churned'].mean()*100
    prod_churn = prod_churn.sort_values(ascending=True)
    axes[1,0].barh(prod_churn.index, prod_churn.values,
        color=['#1D9E75' if v<10 else '#F59E0B' if v<20 else '#EF4444' for v in prod_churn.values],
        edgecolor='white')
    for i, v in enumerate(prod_churn.values):
        axes[1,0].text(v+0.2, i, f'{v:.1f}%', va='center', fontsize=9, fontweight='bold')
    axes[1,0].set_title('Churn Rate by Product', fontweight='bold')
    axes[1,0].set_xlabel('Churn Rate (%)')

    # Device vs churn
    dev_churn = df.groupby('Device')['Churned'].mean()*100
    axes[1,1].bar(dev_churn.index, dev_churn.values,
        color=['#1D9E75','#3B82F6','#F59E0B'], edgecolor='white', width=0.5)
    for i, v in enumerate(dev_churn.values):
        axes[1,1].text(i, v+0.2, f'{v:.1f}%', ha='center', fontsize=9, fontweight='bold')
    axes[1,1].set_title('Churn Rate by Device', fontweight='bold')
    axes[1,1].set_xlabel('Device')
    axes[1,1].set_ylabel('Churn Rate (%)')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/02_churn_drivers.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("[CHART] 02_churn_drivers.png")

def plot_revenue_analysis(df):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle('Revenue Analysis', fontsize=14, fontweight='bold')

    # GGR by country
    country_ggr = df.groupby('Country')['GrossGamingRevenue'].agg(['sum','mean','count'])
    country_ggr = country_ggr.sort_values('sum', ascending=True)
    axes[0].barh(country_ggr.index, country_ggr['sum']/1000, color='#3B82F6', edgecolor='white')
    for i, v in enumerate(country_ggr['sum'].values):
        axes[0].text(v/1000+2, i, f'EUR {v/1000:.0f}K', va='center', fontsize=9)
    axes[0].set_title('Total GGR by Country (EUR K)', fontweight='bold')
    axes[0].set_xlabel('GGR (EUR K)')

    # GGR distribution
    axes[1].hist(df['GrossGamingRevenue'].clip(0, 2000), bins=50,
        color='#1D9E75', edgecolor='white', alpha=0.85)
    axes[1].axvline(df['GrossGamingRevenue'].median(), color='#EF4444',
        linestyle='--', linewidth=2, label=f"Median: EUR {df['GrossGamingRevenue'].median():.0f}")
    axes[1].axvline(df['GrossGamingRevenue'].mean(), color='#F59E0B',
        linestyle='--', linewidth=2, label=f"Mean: EUR {df['GrossGamingRevenue'].mean():.0f}")
    axes[1].set_title('GGR Distribution per Player', fontweight='bold')
    axes[1].set_xlabel('GGR (EUR)')
    axes[1].set_ylabel('Number of Players')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/03_revenue_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("[CHART] 03_revenue_analysis.png")

def export_powerbi(df):
    out = os.path.join(os.path.dirname(__file__), '..', 'data', 'powerbi_ready.csv')
    df.to_csv(out, index=False)
    print(f"[SAVE]  Power BI export -> {out}")

if __name__ == '__main__':
    print("="*55)
    print("ENTAIN PLAYER ANALYTICS — Script 01: EDA")
    print("="*55)
    df = load()
    kpi_summary(df)
    plot_segment_overview(df)
    plot_churn_drivers(df)
    plot_revenue_analysis(df)
    export_powerbi(df)
    print("\nStep 1 complete. Run 02_churn_model.py next.\n")
