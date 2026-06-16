"""
Entain-Style Player Analytics — Script 03: A/B Test Analysis
=============================================================
Simulates and analyses a bonus campaign A/B test.
Measures CTR uplift, conversion rate, and statistical significance.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import os

DATA_PATH  = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_data.csv')
CHARTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'screenshots')

def simulate_ab_test(df):
    """
    Simulate a retention bonus campaign A/B test.
    Control: no bonus offer
    Treatment: 20% deposit bonus offered to At-Risk players
    """
    np.random.seed(123)

    # Select At Risk and Dormant players as target population
    eligible = df[df['PlayerSegment'].isin(['At Risk','Dormant'])].copy()
    n = len(eligible)

    # Random assignment
    eligible['Group'] = np.where(np.random.random(n) < 0.5, 'Treatment', 'Control')

    # Simulate outcomes — treatment group gets uplift
    # Control: base CTR ~18%, conversion ~12%
    # Treatment: CTR ~28% (+55% uplift), conversion ~19%
    base_ctr     = 0.18
    base_conv    = 0.12
    treatment_uplift_ctr  = 0.10
    treatment_uplift_conv = 0.07

    eligible['Clicked'] = np.where(
        eligible['Group'] == 'Treatment',
        (np.random.random(n) < (base_ctr + treatment_uplift_ctr)).astype(int),
        (np.random.random(n) < base_ctr).astype(int)
    )
    eligible['Converted'] = np.where(
        eligible['Group'] == 'Treatment',
        (np.random.random(n) < (base_conv + treatment_uplift_conv)).astype(int),
        (np.random.random(n) < base_conv).astype(int)
    )

    # Simulate revenue impact
    eligible['RevenueImpact'] = np.where(
        eligible['Converted'] == 1,
        np.random.lognormal(4.2, 0.8, n),
        0.0
    )

    return eligible

def analyse_results(test_df):
    results = {}
    for group in ['Control','Treatment']:
        g = test_df[test_df['Group']==group]
        results[group] = {
            'n':          len(g),
            'clicks':     g['Clicked'].sum(),
            'ctr':        g['Clicked'].mean(),
            'conversions':g['Converted'].sum(),
            'conv_rate':  g['Converted'].mean(),
            'revenue':    g['RevenueImpact'].sum(),
            'rev_per_player': g['RevenueImpact'].mean(),
        }

    # Statistical significance — chi-squared for CTR
    ctrl = results['Control']
    trt  = results['Treatment']

    contingency_ctr = np.array([
        [ctrl['clicks'],    ctrl['n'] - ctrl['clicks']],
        [trt['clicks'],     trt['n']  - trt['clicks']]
    ])
    chi2_ctr, p_ctr, _, _ = stats.chi2_contingency(contingency_ctr)

    contingency_conv = np.array([
        [ctrl['conversions'],    ctrl['n'] - ctrl['conversions']],
        [trt['conversions'],     trt['n']  - trt['conversions']]
    ])
    chi2_conv, p_conv, _, _ = stats.chi2_contingency(contingency_conv)

    ctr_uplift  = (trt['ctr']       - ctrl['ctr'])       / ctrl['ctr']  * 100
    conv_uplift = (trt['conv_rate'] - ctrl['conv_rate']) / ctrl['conv_rate'] * 100

    print("\n" + "="*55)
    print("A/B TEST RESULTS — Retention Bonus Campaign")
    print("="*55)
    print(f"Population : At Risk + Dormant players ({ctrl['n']+trt['n']:,} total)")
    print(f"\n{'Metric':<22} {'Control':>12} {'Treatment':>12} {'Uplift':>10}")
    print("-"*58)
    print(f"{'Sample Size':<22} {ctrl['n']:>12,} {trt['n']:>12,}")
    print(f"{'CTR':<22} {ctrl['ctr']:>11.1%} {trt['ctr']:>11.1%} {ctr_uplift:>+9.1f}%")
    print(f"{'Conversion Rate':<22} {ctrl['conv_rate']:>11.1%} {trt['conv_rate']:>11.1%} {conv_uplift:>+9.1f}%")
    print(f"{'Total Revenue':<22} EUR {ctrl['revenue']:>8,.0f} EUR {trt['revenue']:>8,.0f}")
    print(f"{'Rev per Player':<22} EUR {ctrl['rev_per_player']:>8.2f} EUR {trt['rev_per_player']:>8.2f}")
    print("-"*58)
    print(f"CTR p-value        : {p_ctr:.4f}  {'✅ SIGNIFICANT' if p_ctr<0.05 else '❌ NOT SIGNIFICANT'}")
    print(f"Conv p-value       : {p_conv:.4f}  {'✅ SIGNIFICANT' if p_conv<0.05 else '❌ NOT SIGNIFICANT'}")
    print("="*55)

    return results, ctr_uplift, conv_uplift, p_ctr, p_conv

def plot_ab_results(results, ctr_uplift, conv_uplift, p_ctr, p_conv):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle('A/B Test Results — Retention Bonus Campaign', fontsize=13, fontweight='bold')

    groups = ['Control','Treatment']
    colors = ['#6B7280','#1D9E75']

    # CTR
    ctrs = [results[g]['ctr']*100 for g in groups]
    bars = axes[0].bar(groups, ctrs, color=colors, edgecolor='white', width=0.5)
    for bar, val in zip(bars, ctrs):
        axes[0].text(bar.get_x()+bar.get_width()/2, val+0.3, f'{val:.1f}%', ha='center', fontweight='bold')
    axes[0].set_ylabel('Click-Through Rate (%)')
    axes[0].set_title(f'CTR Uplift: {ctr_uplift:+.1f}%\n(p={p_ctr:.4f} {"✅" if p_ctr<0.05 else "❌"})', fontweight='bold')

    # Conversion
    convs = [results[g]['conv_rate']*100 for g in groups]
    bars2 = axes[1].bar(groups, convs, color=colors, edgecolor='white', width=0.5)
    for bar, val in zip(bars2, convs):
        axes[1].text(bar.get_x()+bar.get_width()/2, val+0.2, f'{val:.1f}%', ha='center', fontweight='bold')
    axes[1].set_ylabel('Conversion Rate (%)')
    axes[1].set_title(f'Conversion Uplift: {conv_uplift:+.1f}%\n(p={p_conv:.4f} {"✅" if p_conv<0.05 else "❌"})', fontweight='bold')

    # Revenue
    revs = [results[g]['revenue']/1000 for g in groups]
    bars3 = axes[2].bar(groups, revs, color=colors, edgecolor='white', width=0.5)
    for bar, val in zip(bars3, revs):
        axes[2].text(bar.get_x()+bar.get_width()/2, val+0.5, f'EUR {val:.1f}K', ha='center', fontweight='bold')
    axes[2].set_ylabel('Total Revenue (EUR K)')
    axes[2].set_title('Revenue Impact', fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/06_ab_test_results.png', dpi=150)
    plt.close()
    print("[CHART] 06_ab_test_results.png")

if __name__ == '__main__':
    print("="*55)
    print("ENTAIN PLAYER ANALYTICS — Script 03: A/B Test")
    print("="*55)
    df = pd.read_csv(DATA_PATH)
    test_df = simulate_ab_test(df)
    results, ctr_uplift, conv_uplift, p_ctr, p_conv = analyse_results(test_df)
    plot_ab_results(results, ctr_uplift, conv_uplift, p_ctr, p_conv)
    print("\nStep 3 complete. Run 04_sql_analysis.py next.\n")
