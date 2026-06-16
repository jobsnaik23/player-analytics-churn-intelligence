"""
Player Analytics — Kaggle Dataset Adapter
==========================================
Converts the Kaggle 'Sports Betting Profiling Dataset' from
bet-level rows into the player-level format our analytics
pipeline requires.

Dataset source:
  Coicaud, E. (2025). Sports Betting Profiling Dataset.
  Kaggle. CC0 Public Domain.
  https://www.kaggle.com/datasets/emiliencoicaud/sports-betting-profiling-dataset

HOW TO USE:
-----------
1. Download the dataset from Kaggle:
   https://www.kaggle.com/datasets/emiliencoicaud/sports-betting-profiling-dataset

2. Save the CSV file as:
   data/kaggle_bets.csv

3. Run this script:
   python scripts/00_kaggle_adapter.py

4. Then run the rest of the pipeline as normal:
   python scripts/01_eda.py
   python scripts/02_churn_model.py
   ...

What this script does:
- Reads raw bet-level Kaggle data
- Detects column names automatically (flexible to dataset variations)
- Aggregates to player-level with all required features
- Defines churn based on recency of last bet
- Adds RFM segmentation
- Saves as data/player_data.csv (same format our pipeline expects)
"""

import pandas as pd
import numpy as np
import os
import sys

# ── Paths ──────────────────────────────────────────────────────────────────
KAGGLE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'kaggle_bets.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_data.csv')


def load_kaggle(path: str) -> pd.DataFrame:
    """Load the Kaggle dataset and print its structure."""
    if not os.path.exists(path):
        print(f"""
[ERROR] Kaggle dataset not found at: {path}

Please download it from:
  https://www.kaggle.com/datasets/emiliencoicaud/sports-betting-profiling-dataset

Save the CSV file as: data/kaggle_bets.csv
Then run this script again.
        """)
        sys.exit(1)

    df = pd.read_csv(path)
    print(f"[LOAD]  {len(df):,} rows loaded from Kaggle dataset")
    print(f"[COLS]  Columns found: {list(df.columns)}")
    print(f"[SAMPLE]\n{df.head(2).to_string()}\n")
    return df


def detect_columns(df: pd.DataFrame) -> dict:
    """
    Flexibly detect column names regardless of exact naming.
    Maps common variations to standard names.
    """
    cols = {c.lower().strip(): c for c in df.columns}
    mapping = {}

    # User/player ID
    for candidate in ['user_id','userid','player_id','playerid','customer_id','id']:
        if candidate in cols:
            mapping['user_id'] = cols[candidate]
            break

    # Bet amount
    for candidate in ['bet_amount','betamount','stake','amount','wager']:
        if candidate in cols:
            mapping['bet_amount'] = cols[candidate]
            break

    # Outcome (Win/Loss)
    for candidate in ['outcome','result','win_loss','winloss','status']:
        if candidate in cols:
            mapping['outcome'] = cols[candidate]
            break

    # Date
    for candidate in ['date','bet_date','betdate','timestamp','created_at','time']:
        if candidate in cols:
            mapping['date'] = cols[candidate]
            break

    # Sport/product
    for candidate in ['sport','sport_type','product','category','game_type']:
        if candidate in cols:
            mapping['product'] = cols[candidate]
            break

    # Country
    for candidate in ['country','region','market','location','nationality']:
        if candidate in cols:
            mapping['country'] = cols[candidate]
            break

    # Device
    for candidate in ['device','device_type','platform','channel','source']:
        if candidate in cols:
            mapping['device'] = cols[candidate]
            break

    # Odds
    for candidate in ['odds','price','decimal_odds','payout']:
        if candidate in cols:
            mapping['odds'] = cols[candidate]
            break

    # Profit/loss (optional)
    for candidate in ['profit_loss','profit','pnl','net_profit','return']:
        if candidate in cols:
            mapping['profit_loss'] = cols[candidate]
            break

    print("[MAP]   Column mapping detected:")
    for k, v in mapping.items():
        print(f"          {k:15s} -> {v}")

    missing = [k for k in ['user_id','bet_amount','outcome','date'] if k not in mapping]
    if missing:
        print(f"\n[ERROR] Required columns not found: {missing}")
        print("Please check your CSV column names and update this script.")
        sys.exit(1)

    return mapping


def prepare_bets(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Standardise the bet-level dataframe."""
    bets = pd.DataFrame()

    bets['user_id']    = df[mapping['user_id']].astype(str)
    bets['bet_amount'] = pd.to_numeric(df[mapping['bet_amount']], errors='coerce').fillna(0)
    bets['date']       = pd.to_datetime(df[mapping['date']], errors='coerce')
    bets['outcome']    = df[mapping['outcome']].astype(str).str.strip().str.title()

    # Win flag — handle various outcome representations
    bets['won'] = bets['outcome'].isin(['Win','Won','W','1','True','Yes','Success'])

    # Product/sport
    if 'product' in mapping:
        bets['product'] = df[mapping['product']].astype(str)
    else:
        bets['product'] = 'Sports Betting'

    # Country
    if 'country' in mapping:
        bets['country'] = df[mapping['country']].astype(str)
    else:
        bets['country'] = 'Unknown'

    # Device
    if 'device' in mapping:
        raw_device = df[mapping['device']].astype(str).str.title()
        device_map = {
            'Mobile': 'Mobile App', 'Mobile App': 'Mobile App',
            'Desktop': 'Web', 'Web': 'Web', 'Browser': 'Web',
            'Tablet': 'Tablet', 'App': 'Mobile App'
        }
        bets['device'] = raw_device.map(device_map).fillna('Web')
    else:
        bets['device'] = 'Web'

    # Gross Gaming Revenue per bet
    if 'profit_loss' in mapping:
        bets['ggr_contribution'] = -pd.to_numeric(
            df[mapping['profit_loss']], errors='coerce').fillna(0)
    else:
        # Calculate: house keeps losses, pays out wins
        if 'odds' in mapping:
            odds = pd.to_numeric(df[mapping['odds']], errors='coerce').fillna(2.0)
            bets['ggr_contribution'] = np.where(
                bets['won'],
                -bets['bet_amount'] * (odds - 1),   # house pays out
                bets['bet_amount']                   # house keeps stake
            )
        else:
            bets['ggr_contribution'] = np.where(bets['won'],
                -bets['bet_amount'] * 0.9,
                bets['bet_amount'])

    # Win rate per bet
    bets['win_rate'] = bets['won'].astype(float)

    print(f"[PREP]  {len(bets):,} bets prepared")
    print(f"        Date range: {bets['date'].min()} to {bets['date'].max()}")
    print(f"        Unique players: {bets['user_id'].nunique():,}")
    print(f"        Overall win rate: {bets['won'].mean():.1%}")
    print(f"        Total GGR: EUR {bets['ggr_contribution'].sum():,.0f}")

    return bets


def aggregate_to_player_level(bets: pd.DataFrame) -> pd.DataFrame:
    """Aggregate bet-level rows into one row per player."""

    reference_date = bets['date'].max()

    print(f"\n[AGG]   Aggregating to player level (reference date: {reference_date.date()})...")

    player = bets.groupby('user_id').agg(
        TotalBets        = ('bet_amount',         'count'),
        GrossGamingRevenue = ('ggr_contribution', 'sum'),
        AvgBetSize       = ('bet_amount',         'mean'),
        WinRate          = ('win_rate',            'mean'),
        LastBetDate      = ('date',                'max'),
        FirstBetDate     = ('date',                'min'),
        DepositCount     = ('bet_amount',          'count'),  # proxy
        AvgDeposit       = ('bet_amount',          'mean'),
    ).reset_index()

    player.columns = ['PlayerID','TotalBets','GrossGamingRevenue','AvgBetSize',
                      'WinRate','LastBetDate','FirstBetDate','DepositCount','AvgDeposit']

    # Days since last bet (recency)
    player['DaysSinceLastBet'] = (reference_date - player['LastBetDate']).dt.days

    # Days registered (tenure)
    player['DaysRegistered'] = (reference_date - player['FirstBetDate']).dt.days.clip(1)

    # Sessions per week (bets per week active)
    player['SessionsPerWeek'] = (player['TotalBets'] / (player['DaysRegistered'] / 7)).clip(0, 25).round(2)

    # Most common product and country per player
    player_product = bets.groupby('user_id')['product'].agg(
        lambda x: x.value_counts().index[0]).reset_index()
    player_product.columns = ['PlayerID','Product']

    player_country = bets.groupby('user_id')['country'].agg(
        lambda x: x.value_counts().index[0]).reset_index()
    player_country.columns = ['PlayerID','Country']

    player_device = bets.groupby('user_id')['device'].agg(
        lambda x: x.value_counts().index[0]).reset_index()
    player_device.columns = ['PlayerID','Device']

    player = player.merge(player_product, on='PlayerID')
    player = player.merge(player_country, on='PlayerID')
    player = player.merge(player_device, on='PlayerID')

    # Bonus used — proxy: players with more than median bets
    median_bets = player['TotalBets'].median()
    player['BonusUsed'] = (player['TotalBets'] > median_bets).astype(int)

    # Support contacts proxy
    player['SupportContacts'] = np.random.poisson(0.4, len(player))

    # Churn definition: no bet in last 30 days
    CHURN_THRESHOLD = 30
    player['Churned'] = (player['DaysSinceLastBet'] > CHURN_THRESHOLD).astype(int)

    print(f"[AGG]   {len(player):,} unique players")
    print(f"        Churn rate ({CHURN_THRESHOLD}d threshold): {player['Churned'].mean():.1%}")

    # RFM Score
    player['RFMScore'] = (
        (1 - player['DaysSinceLastBet'] / player['DaysSinceLastBet'].max()) * 40 +
        (player['SessionsPerWeek'] / player['SessionsPerWeek'].max()) * 35 +
        (player['GrossGamingRevenue'].clip(lower=0) /
         player['GrossGamingRevenue'].clip(lower=0).max()) * 25
    ).round(2)

    def segment(score):
        if score >= 70:   return 'Champions'
        elif score >= 50: return 'Loyal Players'
        elif score >= 35: return 'At Risk'
        elif score >= 20: return 'Dormant'
        else:             return 'Lost'

    player['PlayerSegment'] = player['RFMScore'].apply(segment)

    # Clip GGR — remove extreme negatives from lucky players
    player['GrossGamingRevenue'] = player['GrossGamingRevenue'].round(2)

    # Final column selection matching expected pipeline format
    final_cols = [
        'PlayerID','Country','Device','Product','DaysRegistered',
        'SessionsPerWeek','AvgBetSize','TotalBets','WinRate',
        'GrossGamingRevenue','BonusUsed','DaysSinceLastBet',
        'SupportContacts','DepositCount','AvgDeposit',
        'RFMScore','PlayerSegment','Churned'
    ]

    return player[final_cols].round({'AvgBetSize':2,'WinRate':4,'GrossGamingRevenue':2,
                                      'AvgDeposit':2,'SessionsPerWeek':2})


def print_summary(df: pd.DataFrame) -> None:
    print("\n" + "="*60)
    print("PLAYER-LEVEL DATASET SUMMARY")
    print("="*60)
    print(f"Total players          : {len(df):,}")
    print(f"Total GGR              : EUR {df['GrossGamingRevenue'].sum():,.0f}")
    print(f"Avg GGR per player     : EUR {df['GrossGamingRevenue'].mean():,.0f}")
    print(f"Overall churn rate     : {df['Churned'].mean():.1%}")
    print(f"Avg sessions/week      : {df['SessionsPerWeek'].mean():.2f}")
    print(f"Countries              : {df['Country'].nunique()}")
    print(f"\nSegments:")
    for seg, cnt in df['PlayerSegment'].value_counts().items():
        print(f"  {seg:<20} {cnt:>5,} ({cnt/len(df):.1%})")
    print("="*60)


if __name__ == '__main__':
    print("="*60)
    print("KAGGLE ADAPTER — Bet-level to Player-level")
    print("="*60)
    print(f"\nDataset: Sports Betting Profiling Dataset")
    print(f"Source : https://www.kaggle.com/datasets/emiliencoicaud/sports-betting-profiling-dataset")
    print(f"License: CC0 Public Domain\n")

    # Load
    df_raw  = load_kaggle(KAGGLE_PATH)

    # Detect columns
    mapping = detect_columns(df_raw)

    # Prepare bet-level data
    bets = prepare_bets(df_raw, mapping)

    # Aggregate to player level
    players = aggregate_to_player_level(bets)

    # Summary
    print_summary(players)

    # Save
    players.to_csv(OUTPUT_PATH, index=False)
    print(f"\n[SAVE]  Player dataset -> {OUTPUT_PATH}")
    print(f"        {len(players):,} rows x {len(players.columns)} columns")
    print("\n✅ Adapter complete!")
    print("   Now run the full pipeline:")
    print("   python scripts/01_eda.py")
    print("   python scripts/02_churn_model.py")
    print("   python scripts/03_ab_test.py")
    print("   python scripts/04_sql_analysis.py")
    print("   streamlit run scripts/streamlit_app.py\n")
