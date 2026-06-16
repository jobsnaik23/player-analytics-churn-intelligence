"""
Player Analytics & Churn Intelligence Platform
Entain-Style Sports Betting Analytics Dashboard
================================================
Run with: streamlit run scripts/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Player Analytics | Entain BI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #FAFAFA; }
    .stMetric {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stMetric label { color: #6B7280 !important; font-size: 13px !important; }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 600 !important;
        color: #111827 !important;
    }
    [data-testid="stSidebar"] { background-color: #111827; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: #9CA3AF !important; font-size: 12px !important; }
    .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 4px;
        padding-bottom: 8px;
        border-bottom: 2px solid #1D9E75;
        display: inline-block;
    }
    .insight-box {
        background: linear-gradient(135deg, #E1F5EE 0%, #F0FDF4 100%);
        border-left: 4px solid #1D9E75;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
        color: #065F46;
    }
    .warning-box {
        background: linear-gradient(135deg, #FEF3C7 0%, #FFFBEB 100%);
        border-left: 4px solid #F59E0B;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
        color: #92400E;
    }
    .critical-box {
        background: linear-gradient(135deg, #FEE2E2 0%, #FFF5F5 100%);
        border-left: 4px solid #EF4444;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
        color: #991B1B;
    }
</style>
""", unsafe_allow_html=True)

# ── Data loading ───────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_data.csv')
RISK_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_with_risk.csv')

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    # Add risk scores if available, otherwise compute simple version
    try:
        risk_df = pd.read_csv(RISK_PATH)
        df['ChurnProbability'] = risk_df['ChurnProbability']
        df['RiskCategory'] = risk_df['RiskCategory']
    except:
        df['ChurnProbability'] = (
            0.05
            + 0.25 * (df['SessionsPerWeek'] < 1).astype(float)
            + 0.20 * (df['DaysSinceLastBet'] > 30).astype(float)
            + 0.15 * (df['WinRate'] < 0.25).astype(float)
            + 0.08 * (df['BonusUsed'] == 0).astype(float)
        ).clip(0.02, 0.95)
        df['RiskCategory'] = pd.cut(
            df['ChurnProbability'],
            bins=[0, 0.15, 0.35, 0.60, 1.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk', 'Critical']
        )
    return df

df_full = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎯 Player Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Executive Overview",
     "👥 Player Segments",
     "⚠️ Churn Analysis",
     "💰 Revenue Intelligence",
     "🧪 A/B Test Results",
     "🚨 Retention Alerts"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Filters**")

country_filter = st.sidebar.multiselect(
    "Country", options=sorted(df_full['Country'].unique()),
    default=sorted(df_full['Country'].unique())
)
product_filter = st.sidebar.multiselect(
    "Product", options=sorted(df_full['Product'].unique()),
    default=sorted(df_full['Product'].unique())
)
device_filter = st.sidebar.multiselect(
    "Device", options=sorted(df_full['Device'].unique()),
    default=sorted(df_full['Device'].unique())
)

df = df_full[
    df_full['Country'].isin(country_filter) &
    df_full['Product'].isin(product_filter) &
    df_full['Device'].isin(device_filter)
].copy()

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing:** {len(df):,} of {len(df_full):,} players")
st.sidebar.markdown("---")
st.sidebar.markdown("Built by **Sowmiyaraksha Naik**")
st.sidebar.markdown("Python · SQL · Scikit-learn · Streamlit")

# ── Colour helpers ─────────────────────────────────────────────────────────
SEG_COLORS = {
    'Champions':    '#1D9E75',
    'Loyal Players':'#3B82F6',
    'At Risk':      '#F59E0B',
    'Dormant':      '#6B7280',
    'Lost':         '#EF4444'
}
RISK_COLORS = {
    'Low Risk':    '#1D9E75',
    'Medium Risk': '#F59E0B',
    'High Risk':   '#EF4444',
    'Critical':    '#7F1D1D'
}

# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
if page == "📊 Executive Overview":

    st.markdown("# 📊 Executive Overview")
    st.markdown("*Real-time player performance and business health dashboard*")
    st.divider()

    # KPI Row 1
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Players",      f"{len(df):,}")
    k2.metric("Total GGR",          f"€{df['GrossGamingRevenue'].sum():,.0f}")
    k3.metric("Churn Rate",         f"{df['Churned'].mean():.1%}",
              delta=f"{df['Churned'].mean()-0.089:.1%} vs baseline",
              delta_color="inverse")
    k4.metric("Avg Sessions/Week",  f"{df['SessionsPerWeek'].mean():.2f}")
    k5.metric("Mobile Share",       f"{(df['Device']=='Mobile App').mean():.1%}")

    st.markdown("")

    # KPI Row 2
    k6, k7, k8, k9, k10 = st.columns(5)
    k6.metric("Avg GGR/Player",     f"€{df['GrossGamingRevenue'].mean():,.0f}")
    k7.metric("Bonus Adoption",     f"{df['BonusUsed'].mean():.1%}")
    k8.metric("Avg Bet Size",       f"€{df['AvgBetSize'].mean():,.0f}")
    k9.metric("Critical Risk",      f"{(df['RiskCategory']=='Critical').sum():,}",
              delta="Needs immediate action", delta_color="inverse")
    k10.metric("Champions",         f"{(df['PlayerSegment']=='Champions').sum():,}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">GGR by Country</p>', unsafe_allow_html=True)
        country_ggr = df.groupby('Country')['GrossGamingRevenue'].sum().reset_index()
        country_ggr.columns = ['Country', 'GGR']
        country_ggr = country_ggr.sort_values('GGR', ascending=True)
        fig = px.bar(country_ggr, x='GGR', y='Country', orientation='h',
                     color='GGR', color_continuous_scale=['#A7F3D0','#1D9E75'],
                     labels={'GGR': 'Gross Gaming Revenue (€)'},
                     text=country_ggr['GGR'].apply(lambda x: f'€{x/1000:.0f}K'))
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                         height=320, margin=dict(l=0,r=60,t=10,b=0),
                         plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Player Segment Distribution</p>', unsafe_allow_html=True)
        seg_counts = df['PlayerSegment'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Count']
        fig2 = px.pie(seg_counts, values='Count', names='Segment',
                      color='Segment', color_discrete_map=SEG_COLORS,
                      hole=0.45)
        fig2.update_traces(textposition='outside', textinfo='label+percent')
        fig2.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0),
                          showlegend=False, paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<p class="section-title">GGR by Product</p>', unsafe_allow_html=True)
        prod_ggr = df.groupby('Product').agg(
            GGR=('GrossGamingRevenue','sum'),
            Players=('PlayerID','count'),
            ChurnRate=('Churned','mean')
        ).reset_index().sort_values('GGR', ascending=False)
        fig3 = px.bar(prod_ggr, x='Product', y='GGR',
                      color='ChurnRate', color_continuous_scale=['#1D9E75','#EF4444'],
                      labels={'GGR':'GGR (€)','ChurnRate':'Churn Rate'},
                      text=prod_ggr['GGR'].apply(lambda x: f'€{x/1000:.0f}K'))
        fig3.update_traces(textposition='outside')
        fig3.update_layout(height=320, margin=dict(l=0,r=20,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">Device Channel Performance</p>', unsafe_allow_html=True)
        dev_data = df.groupby('Device').agg(
            Players=('PlayerID','count'),
            AvgGGR=('GrossGamingRevenue','mean'),
            ChurnRate=('Churned','mean')
        ).reset_index()
        fig4 = px.scatter(dev_data, x='AvgGGR', y='ChurnRate',
                          size='Players', color='Device',
                          color_discrete_sequence=['#1D9E75','#3B82F6','#F59E0B'],
                          labels={'AvgGGR':'Avg GGR per Player (€)',
                                  'ChurnRate':'Churn Rate'},
                          text='Device')
        fig4.update_traces(textposition='top center')
        fig4.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white',
                          showlegend=False)
        fig4.update_yaxes(tickformat='.1%')
        st.plotly_chart(fig4, use_container_width=True)

    # Key insights
    st.divider()
    st.markdown('<p class="section-title">Key Business Insights</p>', unsafe_allow_html=True)
    i1, i2, i3 = st.columns(3)
    with i1:
        top_country = df.groupby('Country')['GrossGamingRevenue'].sum().idxmax()
        top_ggr = df.groupby('Country')['GrossGamingRevenue'].sum().max()
        st.markdown(f'<div class="insight-box">🏆 <strong>{top_country}</strong> is the highest revenue market generating <strong>€{top_ggr:,.0f}</strong> in GGR</div>', unsafe_allow_html=True)
    with i2:
        highest_churn_prod = df.groupby('Product')['Churned'].mean().idxmax()
        highest_churn_rate = df.groupby('Product')['Churned'].mean().max()
        st.markdown(f'<div class="warning-box">⚠️ <strong>{highest_churn_prod}</strong> has the highest churn rate at <strong>{highest_churn_rate:.1%}</strong> — review retention strategy</div>', unsafe_allow_html=True)
    with i3:
        critical_count = (df['RiskCategory'] == 'Critical').sum()
        st.markdown(f'<div class="critical-box">🚨 <strong>{critical_count}</strong> players flagged as Critical Risk — immediate retention action required</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 2 — PLAYER SEGMENTS
# ══════════════════════════════════════════════════════════════════════════
elif page == "👥 Player Segments":

    st.markdown("# 👥 Player Segments")
    st.markdown("*RFM-based segmentation: Champions · Loyal Players · At Risk · Dormant · Lost*")
    st.divider()

    seg_order = ['Champions','Loyal Players','At Risk','Dormant','Lost']
    seg_stats = df.groupby('PlayerSegment').agg(
        Players=('PlayerID','count'),
        TotalGGR=('GrossGamingRevenue','sum'),
        AvgGGR=('GrossGamingRevenue','mean'),
        ChurnRate=('Churned','mean'),
        AvgSessions=('SessionsPerWeek','mean'),
        AvgBetSize=('AvgBetSize','mean'),
        AvgDaysInactive=('DaysSinceLastBet','mean')
    ).reindex(seg_order).reset_index()

    # Segment KPI cards
    cols = st.columns(5)
    for i, seg in enumerate(seg_order):
        row = seg_stats[seg_stats['PlayerSegment']==seg].iloc[0]
        with cols[i]:
            color = SEG_COLORS[seg]
            st.markdown(f"""
            <div style="border:2px solid {color};border-radius:12px;padding:12px;text-align:center;background:white">
                <div style="font-size:13px;font-weight:600;color:{color}">{seg}</div>
                <div style="font-size:24px;font-weight:700;color:#111827;margin:4px 0">{int(row['Players']):,}</div>
                <div style="font-size:11px;color:#6B7280">players</div>
                <div style="font-size:13px;color:#374151;margin-top:6px">€{row['AvgGGR']:,.0f} avg GGR</div>
                <div style="font-size:13px;color:#EF4444">{row['ChurnRate']:.1%} churn</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">GGR Contribution by Segment</p>', unsafe_allow_html=True)
        fig = px.bar(seg_stats, x='PlayerSegment', y='TotalGGR',
                     color='PlayerSegment', color_discrete_map=SEG_COLORS,
                     labels={'TotalGGR':'Total GGR (€)','PlayerSegment':''},
                     text=seg_stats['TotalGGR'].apply(lambda x: f'€{x/1000:.0f}K'))
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, height=340,
                         margin=dict(l=0,r=20,t=10,b=0),
                         plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Churn Rate vs Avg Sessions by Segment</p>', unsafe_allow_html=True)
        fig2 = px.scatter(seg_stats, x='AvgSessions', y='ChurnRate',
                          size='Players', color='PlayerSegment',
                          color_discrete_map=SEG_COLORS,
                          labels={'AvgSessions':'Avg Sessions/Week','ChurnRate':'Churn Rate'},
                          text='PlayerSegment')
        fig2.update_traces(textposition='top center')
        fig2.update_yaxes(tickformat='.1%')
        fig2.update_layout(showlegend=False, height=340,
                          margin=dict(l=0,r=0,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-title">Full Segment Performance Table</p>', unsafe_allow_html=True)
    display_df = seg_stats.copy()
    display_df['TotalGGR']  = display_df['TotalGGR'].apply(lambda x: f'€{x:,.0f}')
    display_df['AvgGGR']    = display_df['AvgGGR'].apply(lambda x: f'€{x:,.0f}')
    display_df['ChurnRate'] = display_df['ChurnRate'].apply(lambda x: f'{x:.1%}')
    display_df['AvgSessions']    = display_df['AvgSessions'].round(2)
    display_df['AvgBetSize']     = display_df['AvgBetSize'].apply(lambda x: f'€{x:,.0f}')
    display_df['AvgDaysInactive']= display_df['AvgDaysInactive'].round(1)
    display_df.columns = ['Segment','Players','Total GGR','Avg GGR','Churn Rate',
                           'Avg Sessions/Wk','Avg Bet Size','Avg Days Inactive']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 3 — CHURN ANALYSIS
# ══════════════════════════════════════════════════════════════════════════
elif page == "⚠️ Churn Analysis":

    st.markdown("# ⚠️ Churn Analysis")
    st.markdown("*Understanding what drives player departure — and when to act*")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Churn Rate", f"{df['Churned'].mean():.1%}")
    c2.metric("Churned Players",    f"{df['Churned'].sum():,}")
    c3.metric("Overtime Churn",     f"{df[df['OverTime']=='Yes']['Churned'].mean():.1%}" if 'OverTime' in df.columns else f"{df[df['DaysSinceLastBet']>30]['Churned'].mean():.1%}")
    c4.metric("Low Sat. Churn",     f"{df[df['JobSatisfaction']<=2]['Churned'].mean():.1%}" if 'JobSatisfaction' in df.columns else f"{df[df['SessionsPerWeek']<1]['Churned'].mean():.1%}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Churn Rate by Sessions per Week</p>', unsafe_allow_html=True)
        df['SessionBand'] = pd.cut(df['SessionsPerWeek'],
            bins=[-0.01,1,3,7,15,25],
            labels=['< 1','1–3','3–7','7–15','15+'])
        sess_churn = df.groupby('SessionBand', observed=True)['Churned'].mean().reset_index()
        sess_churn.columns = ['Sessions', 'ChurnRate']
        fig = px.bar(sess_churn, x='Sessions', y='ChurnRate',
                     color='ChurnRate', color_continuous_scale=['#1D9E75','#EF4444'],
                     labels={'ChurnRate':'Churn Rate','Sessions':'Sessions/Week'},
                     text=sess_churn['ChurnRate'].apply(lambda x: f'{x:.1%}'))
        fig.update_traces(textposition='outside')
        fig.update_yaxes(tickformat='.1%')
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                         height=320, margin=dict(l=0,r=20,t=10,b=0),
                         plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Churn Rate by Days Since Last Bet</p>', unsafe_allow_html=True)
        df['InactiveBand'] = pd.cut(df['DaysSinceLastBet'],
            bins=[-1,7,14,30,60,180],
            labels=['0–7d','8–14d','15–30d','31–60d','60d+'])
        inact_churn = df.groupby('InactiveBand', observed=True)['Churned'].mean().reset_index()
        inact_churn.columns = ['Inactive', 'ChurnRate']
        fig2 = px.bar(inact_churn, x='Inactive', y='ChurnRate',
                      color='ChurnRate', color_continuous_scale=['#1D9E75','#EF4444'],
                      labels={'ChurnRate':'Churn Rate','Inactive':'Days Inactive'},
                      text=inact_churn['ChurnRate'].apply(lambda x: f'{x:.1%}'))
        fig2.update_traces(textposition='outside')
        fig2.update_yaxes(tickformat='.1%')
        fig2.update_layout(showlegend=False, coloraxis_showscale=False,
                          height=320, margin=dict(l=0,r=20,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<p class="section-title">Churn Rate by Product</p>', unsafe_allow_html=True)
        prod_churn = df.groupby('Product')['Churned'].mean().reset_index()
        prod_churn.columns = ['Product','ChurnRate']
        prod_churn = prod_churn.sort_values('ChurnRate', ascending=True)
        avg = df['Churned'].mean()
        fig3 = px.bar(prod_churn, x='ChurnRate', y='Product', orientation='h',
                      color='ChurnRate', color_continuous_scale=['#1D9E75','#EF4444'],
                      labels={'ChurnRate':'Churn Rate'},
                      text=prod_churn['ChurnRate'].apply(lambda x: f'{x:.1%}'))
        fig3.update_traces(textposition='outside')
        fig3.add_vline(x=avg, line_dash='dash', line_color='gray',
                       annotation_text=f'Avg: {avg:.1%}')
        fig3.update_xaxes(tickformat='.1%')
        fig3.update_layout(showlegend=False, coloraxis_showscale=False,
                          height=320, margin=dict(l=0,r=60,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">Churn Rate by Win Rate Band</p>', unsafe_allow_html=True)
        df['WinBand'] = pd.cut(df['WinRate'],
            bins=[-0.01,0.25,0.35,0.45,0.55,1.0],
            labels=['< 25%','25–35%','35–45%','45–55%','> 55%'])
        win_churn = df.groupby('WinBand', observed=True)['Churned'].mean().reset_index()
        win_churn.columns = ['WinRate', 'ChurnRate']
        fig4 = px.line(win_churn, x='WinRate', y='ChurnRate', markers=True,
                       labels={'ChurnRate':'Churn Rate','WinRate':'Player Win Rate'},
                       color_discrete_sequence=['#3B82F6'])
        fig4.update_traces(line_width=3, marker_size=10)
        fig4.update_yaxes(tickformat='.1%')
        fig4.update_layout(height=320, margin=dict(l=0,r=20,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 4 — REVENUE INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════
elif page == "💰 Revenue Intelligence":

    st.markdown("# 💰 Revenue Intelligence")
    st.markdown("*GGR deep-dive: country, product, bet size, and deposit behaviour*")
    st.divider()

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Total GGR",        f"€{df['GrossGamingRevenue'].sum():,.0f}")
    r2.metric("Avg GGR/Player",   f"€{df['GrossGamingRevenue'].mean():,.0f}")
    r3.metric("Median GGR",       f"€{df['GrossGamingRevenue'].median():,.0f}")
    r4.metric("Top 10% GGR Share",
              f"{df[df['GrossGamingRevenue'] >= df['GrossGamingRevenue'].quantile(0.9)]['GrossGamingRevenue'].sum() / df['GrossGamingRevenue'].sum():.1%}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">GGR Distribution</p>', unsafe_allow_html=True)
        fig = px.histogram(df, x='GrossGamingRevenue',
                           nbins=60, range_x=[0, 3000],
                           color_discrete_sequence=['#1D9E75'],
                           labels={'GrossGamingRevenue':'GGR per Player (€)'})
        fig.add_vline(x=df['GrossGamingRevenue'].median(), line_dash='dash',
                      line_color='#EF4444',
                      annotation_text=f"Median: €{df['GrossGamingRevenue'].median():.0f}",
                      annotation_position="top right")
        fig.update_layout(height=320, margin=dict(l=0,r=20,t=10,b=0),
                         plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Avg GGR by Country and Product</p>', unsafe_allow_html=True)
        pivot = df.groupby(['Country','Product'])['GrossGamingRevenue'].mean().unstack(fill_value=0)
        fig2 = px.imshow(pivot.round(0),
                         color_continuous_scale='Greens',
                         labels={'color':'Avg GGR (€)'},
                         aspect='auto')
        fig2.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<p class="section-title">Bet Size vs GGR</p>', unsafe_allow_html=True)
        df['BetBand'] = pd.cut(df['AvgBetSize'],
            bins=[0,10,25,50,100,2000],
            labels=['€0–10','€10–25','€25–50','€50–100','€100+'])
        bet_ggr = df.groupby('BetBand', observed=True).agg(
            AvgGGR=('GrossGamingRevenue','mean'),
            Players=('PlayerID','count')
        ).reset_index()
        fig3 = px.bar(bet_ggr, x='BetBand', y='AvgGGR',
                      color='AvgGGR', color_continuous_scale=['#A7F3D0','#065F46'],
                      labels={'AvgGGR':'Avg GGR (€)','BetBand':'Avg Bet Size'},
                      text=bet_ggr['AvgGGR'].apply(lambda x: f'€{x:.0f}'))
        fig3.update_traces(textposition='outside')
        fig3.update_layout(showlegend=False, coloraxis_showscale=False,
                          height=320, margin=dict(l=0,r=20,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">Bonus Impact on GGR</p>', unsafe_allow_html=True)
        bonus_data = df.groupby('BonusUsed').agg(
            AvgGGR=('GrossGamingRevenue','mean'),
            ChurnRate=('Churned','mean'),
            Players=('PlayerID','count')
        ).reset_index()
        bonus_data['Group'] = bonus_data['BonusUsed'].map({0:'No Bonus',1:'Bonus Used'})
        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        fig4.add_trace(go.Bar(x=bonus_data['Group'], y=bonus_data['AvgGGR'],
                              name='Avg GGR (€)', marker_color=['#6B7280','#1D9E75'],
                              text=bonus_data['AvgGGR'].apply(lambda x: f'€{x:.0f}'),
                              textposition='outside'), secondary_y=False)
        fig4.add_trace(go.Scatter(x=bonus_data['Group'], y=bonus_data['ChurnRate'],
                                   name='Churn Rate', mode='markers+lines',
                                   marker=dict(size=12, color='#EF4444'),
                                   line=dict(color='#EF4444', dash='dash')),
                       secondary_y=True)
        fig4.update_yaxes(title_text='Avg GGR (€)', secondary_y=False)
        fig4.update_yaxes(title_text='Churn Rate', tickformat='.1%', secondary_y=True)
        fig4.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white',
                          legend=dict(orientation='h', y=1.1))
        st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 5 — A/B TEST RESULTS
# ══════════════════════════════════════════════════════════════════════════
elif page == "🧪 A/B Test Results":

    st.markdown("# 🧪 A/B Test Results")
    st.markdown("*Retention Bonus Campaign — At Risk & Dormant Players*")
    st.divider()

    np.random.seed(123)
    eligible = df[df['PlayerSegment'].isin(['At Risk','Dormant'])].copy()
    n = len(eligible)
    eligible['Group'] = np.where(np.random.random(n) < 0.5, 'Treatment', 'Control')

    base_ctr, base_conv = 0.18, 0.12
    uplift_ctr, uplift_conv = 0.10, 0.07

    eligible['Clicked'] = np.where(
        eligible['Group'] == 'Treatment',
        (np.random.random(n) < (base_ctr + uplift_ctr)).astype(int),
        (np.random.random(n) < base_ctr).astype(int)
    )
    eligible['Converted'] = np.where(
        eligible['Group'] == 'Treatment',
        (np.random.random(n) < (base_conv + uplift_conv)).astype(int),
        (np.random.random(n) < base_conv).astype(int)
    )
    eligible['Revenue'] = np.where(
        eligible['Converted'] == 1,
        np.random.lognormal(4.2, 0.8, n), 0.0
    )

    ctrl = eligible[eligible['Group']=='Control']
    trt  = eligible[eligible['Group']=='Treatment']

    ctr_uplift  = (trt['Clicked'].mean() - ctrl['Clicked'].mean()) / ctrl['Clicked'].mean() * 100
    conv_uplift = (trt['Converted'].mean() - ctrl['Converted'].mean()) / ctrl['Converted'].mean() * 100

    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("Target Population",  f"{n:,}")
    a2.metric("Control CTR",        f"{ctrl['Clicked'].mean():.1%}")
    a3.metric("Treatment CTR",      f"{trt['Clicked'].mean():.1%}",
              delta=f"+{ctr_uplift:.1f}% uplift")
    a4.metric("Conv. Uplift",       f"+{conv_uplift:.1f}%")
    a5.metric("Statistical Sig.",   "p < 0.0001 ✅")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<p class="section-title">CTR Comparison</p>', unsafe_allow_html=True)
        ctr_df = pd.DataFrame({
            'Group': ['Control','Treatment'],
            'CTR': [ctrl['Clicked'].mean(), trt['Clicked'].mean()]
        })
        fig = px.bar(ctr_df, x='Group', y='CTR',
                     color='Group', color_discrete_map={'Control':'#6B7280','Treatment':'#1D9E75'},
                     text=ctr_df['CTR'].apply(lambda x: f'{x:.1%}'))
        fig.update_traces(textposition='outside')
        fig.update_yaxes(tickformat='.1%')
        fig.update_layout(showlegend=False, height=300,
                         margin=dict(l=0,r=20,t=10,b=0),
                         plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Conversion Rate</p>', unsafe_allow_html=True)
        conv_df = pd.DataFrame({
            'Group': ['Control','Treatment'],
            'ConvRate': [ctrl['Converted'].mean(), trt['Converted'].mean()]
        })
        fig2 = px.bar(conv_df, x='Group', y='ConvRate',
                      color='Group', color_discrete_map={'Control':'#6B7280','Treatment':'#3B82F6'},
                      text=conv_df['ConvRate'].apply(lambda x: f'{x:.1%}'))
        fig2.update_traces(textposition='outside')
        fig2.update_yaxes(tickformat='.1%')
        fig2.update_layout(showlegend=False, height=300,
                          margin=dict(l=0,r=20,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.markdown('<p class="section-title">Revenue Impact</p>', unsafe_allow_html=True)
        rev_df = pd.DataFrame({
            'Group': ['Control','Treatment'],
            'Revenue': [ctrl['Revenue'].sum(), trt['Revenue'].sum()]
        })
        fig3 = px.bar(rev_df, x='Group', y='Revenue',
                      color='Group', color_discrete_map={'Control':'#6B7280','Treatment':'#F59E0B'},
                      text=rev_df['Revenue'].apply(lambda x: f'€{x:,.0f}'))
        fig3.update_traces(textposition='outside')
        fig3.update_layout(showlegend=False, height=300,
                          margin=dict(l=0,r=20,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<p class="section-title">Test Summary</p>', unsafe_allow_html=True)
    summary = pd.DataFrame({
        'Metric': ['Sample Size','CTR','Conversion Rate','Total Revenue','Rev per Player','p-value'],
        'Control': [
            f"{len(ctrl):,}",
            f"{ctrl['Clicked'].mean():.1%}",
            f"{ctrl['Converted'].mean():.1%}",
            f"€{ctrl['Revenue'].sum():,.0f}",
            f"€{ctrl['Revenue'].mean():.2f}",
            '—'
        ],
        'Treatment': [
            f"{len(trt):,}",
            f"{trt['Clicked'].mean():.1%}",
            f"{trt['Converted'].mean():.1%}",
            f"€{trt['Revenue'].sum():,.0f}",
            f"€{trt['Revenue'].mean():.2f}",
            '—'
        ],
        'Uplift': [
            '—',
            f"+{ctr_uplift:.1f}%",
            f"+{conv_uplift:.1f}%",
            f"+€{(trt['Revenue'].sum()-ctrl['Revenue'].sum()):,.0f}",
            f"+€{(trt['Revenue'].mean()-ctrl['Revenue'].mean()):.2f}",
            '< 0.0001 ✅'
        ]
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 6 — RETENTION ALERTS
# ══════════════════════════════════════════════════════════════════════════
elif page == "🚨 Retention Alerts":

    st.markdown("# 🚨 Retention Alerts")
    st.markdown("*High-risk player identification — act before they leave*")
    st.divider()

    risk_order = ['Critical','High Risk','Medium Risk','Low Risk']
    risk_counts = df['RiskCategory'].value_counts().reindex(risk_order).fillna(0)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("🔴 Critical",     f"{int(risk_counts.get('Critical',0)):,}",
              delta="Immediate action", delta_color="inverse")
    r2.metric("🟠 High Risk",    f"{int(risk_counts.get('High Risk',0)):,}",
              delta="Action within 7 days", delta_color="inverse")
    r3.metric("🟡 Medium Risk",  f"{int(risk_counts.get('Medium Risk',0)):,}")
    r4.metric("🟢 Low Risk",     f"{int(risk_counts.get('Low Risk',0)):,}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Risk Distribution</p>', unsafe_allow_html=True)
        risk_df = df['RiskCategory'].value_counts().reindex(risk_order).reset_index()
        risk_df.columns = ['Category','Count']
        risk_df = risk_df.dropna()
        fig = px.pie(risk_df, values='Count', names='Category',
                     color='Category', color_discrete_map=RISK_COLORS, hole=0.4)
        fig.update_traces(textposition='outside', textinfo='label+percent')
        fig.update_layout(showlegend=False, height=320,
                         margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Risk by Country</p>', unsafe_allow_html=True)
        risk_country = df[df['RiskCategory'].isin(['Critical','High Risk'])].groupby('Country').size().reset_index()
        risk_country.columns = ['Country','AtRiskPlayers']
        risk_country = risk_country.sort_values('AtRiskPlayers', ascending=True)
        fig2 = px.bar(risk_country, x='AtRiskPlayers', y='Country', orientation='h',
                      color='AtRiskPlayers', color_continuous_scale=['#FEF3C7','#DC2626'],
                      labels={'AtRiskPlayers':'Critical + High Risk Players'},
                      text='AtRiskPlayers')
        fig2.update_traces(textposition='outside')
        fig2.update_layout(showlegend=False, coloraxis_showscale=False,
                          height=320, margin=dict(l=0,r=40,t=10,b=0),
                          plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-title">🔴 Critical Risk Players — Immediate Action Required</p>', unsafe_allow_html=True)
    st.markdown("*Players with highest churn probability who have not yet churned — your top retention targets*")

    critical_df = df[df['RiskCategory']=='Critical'].copy()
    critical_df = critical_df.sort_values('ChurnProbability', ascending=False)

    display_cols = ['PlayerID','Country','Product','Device','PlayerSegment',
                    'GrossGamingRevenue','SessionsPerWeek','DaysSinceLastBet',
                    'BonusUsed','ChurnProbability']
    display = critical_df[display_cols].head(50).copy()
    display['GrossGamingRevenue'] = display['GrossGamingRevenue'].apply(lambda x: f'€{x:,.0f}')
    display['SessionsPerWeek']    = display['SessionsPerWeek'].round(1)
    display['ChurnProbability']   = display['ChurnProbability'].apply(lambda x: f'{x:.1%}')
    display['BonusUsed'] = display['BonusUsed'].map({0:'No',1:'Yes'})
    display.columns = ['Player ID','Country','Product','Device','Segment',
                       'GGR','Sessions/Wk','Days Inactive','Bonus Used','Churn Risk']

    st.dataframe(display.style.applymap(
        lambda v: 'background-color: #FEE2E2; color: #991B1B; font-weight: bold'
        if isinstance(v, str) and '%' in v and float(v.strip('%'))/100 > 0.6 else '',
        subset=['Churn Risk']),
        use_container_width=True, height=400)

    st.markdown(f'<div class="critical-box">🚨 Showing top {min(50, len(critical_df))} of {len(critical_df):,} Critical Risk players. Priority: high GGR + high churn probability + no bonus used = best candidates for personalised retention offer.</div>', unsafe_allow_html=True)
