"""
Entain-Style Player Analytics — Script 02: Churn Prediction Model
=================================================================
Trains and evaluates ML models to predict player churn.
Outputs feature importance, ROC curves, and risk scores.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, os

from sklearn.model_selection   import train_test_split, cross_val_score
from sklearn.preprocessing     import StandardScaler, LabelEncoder
from sklearn.ensemble          import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model      import LogisticRegression
from sklearn.metrics           import (classification_report, roc_auc_score,
                                        roc_curve, confusion_matrix)

DATA_PATH    = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_data.csv')
CHARTS_DIR   = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
METRICS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'model_metrics.json')

FEATURES = ['SessionsPerWeek','AvgBetSize','TotalBets','WinRate',
            'DaysSinceLastBet','BonusUsed','DepositCount','AvgDeposit','DaysRegistered']

def prepare(df):
    X = df[FEATURES].copy()
    y = df['Churned']
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

def train_models(X_train, X_test, y_train, y_test):
    models = {
        'Logistic Regression':  LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest':        RandomForestClassifier(n_estimators=150, random_state=42),
        'Gradient Boosting':    GradientBoostingClassifier(n_estimators=150, random_state=42),
    }
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:,1]
        auc    = roc_auc_score(y_test, y_prob)
        cv     = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc').mean()
        report = classification_report(y_test, y_pred, output_dict=True)
        results[name] = {'model':model,'auc':auc,'cv':cv,'y_prob':y_prob,
                         'acc':report['accuracy'],'f1':report['1']['f1-score']}
        print(f"[MODEL] {name:25s} AUC: {auc:.3f}  CV AUC: {cv:.3f}  Acc: {report['accuracy']:.3f}")
    return results

def plot_roc(results, y_test):
    fig, ax = plt.subplots(figsize=(8,6))
    colors = ['#3B82F6','#1D9E75','#F59E0B']
    for (name, res), color in zip(results.items(), colors):
        fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
        ax.plot(fpr, tpr, color=color, lw=2, label=f"{name} (AUC={res['auc']:.3f})")
    ax.plot([0,1],[0,1],'k--',alpha=0.4,label='Random baseline')
    ax.set_xlabel('False Positive Rate'); ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curves — Player Churn Prediction', fontsize=13, fontweight='bold')
    ax.legend(); ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/04_roc_curves.png', dpi=150)
    plt.close()
    print("[CHART] 04_roc_curves.png")

def plot_feature_importance(results):
    rf = results['Random Forest']['model']
    imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9,5))
    colors = ['#EF4444' if v>0.12 else '#1D9E75' for v in imp.values]
    ax.barh(imp.index, imp.values, color=colors, edgecolor='white')
    for bar, val in zip(ax.patches, imp.values):
        ax.text(val+0.003, bar.get_y()+bar.get_height()/2, f'{val:.3f}', va='center', fontsize=9)
    ax.set_xlabel('Feature Importance Score')
    ax.set_title('Top Churn Predictors — Random Forest', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/05_feature_importance.png', dpi=150)
    plt.close()
    print("[CHART] 05_feature_importance.png")

def add_risk_scores(df, results):
    best_model = results['Gradient Boosting']['model']
    X = df[FEATURES]
    df['ChurnProbability'] = best_model.predict_proba(X)[:,1]
    df['RiskCategory'] = pd.cut(df['ChurnProbability'],
        bins=[0, 0.15, 0.35, 0.60, 1.0],
        labels=['Low Risk','Medium Risk','High Risk','Critical'])
    out = os.path.join(os.path.dirname(__file__), '..', 'data', 'player_with_risk.csv')
    df.to_csv(out, index=False)
    print(f"[SAVE]  Risk scores added -> {out}")
    print(f"        Critical risk: {(df['RiskCategory']=='Critical').sum():,} players")
    print(f"        High risk:     {(df['RiskCategory']=='High Risk').sum():,} players")
    return df

def save_metrics(results):
    metrics = {k: {'auc':v['auc'],'cv':v['cv'],'acc':v['acc'],'f1':v['f1']}
               for k,v in results.items()}
    best = max(results.items(), key=lambda x: x[1]['auc'])
    metrics['best_model'] = best[0]
    metrics['best_auc']   = best[1]['auc']
    with open(METRICS_PATH,'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"[SAVE]  Metrics -> {METRICS_PATH}")
    print(f"[BEST]  {best[0]} (AUC: {best[1]['auc']:.3f})")

if __name__ == '__main__':
    print("="*55)
    print("ENTAIN PLAYER ANALYTICS — Script 02: Churn Model")
    print("="*55)
    df = pd.read_csv(DATA_PATH)
    X_train, X_test, y_train, y_test = prepare(df)
    print(f"[SPLIT] Train: {len(X_train):,}  Test: {len(X_test):,}")
    results = train_models(X_train, X_test, y_train, y_test)
    plot_roc(results, y_test)
    plot_feature_importance(results)
    df = add_risk_scores(df, results)
    save_metrics(results)
    print("\nStep 2 complete. Run 03_ab_test.py next.\n")
