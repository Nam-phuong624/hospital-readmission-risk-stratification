#!/usr/bin/env python3
"""
Phase 3: Root Cause Analysis (Nguyên nhân & Yếu tố gắn với tái nhập viện)
- Phân tích đa biến (Odds Ratios, p-value) để xác định các yếu tố nguy cơ độc lập.
- Phân nhóm mã chẩn đoán ICD-9 (diag_1): Tuần hoàn, Đái tháo đường, Hô hấp, Tiêu hóa, Thận - Tiết niệu,...
- Đánh giá tác động của chế độ dùng thuốc (Insulin, thay đổi phác đồ).
- Lưu kết quả ra outputs/tables/ và outputs/figures/.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from scipy import stats

# Paths
DATA_PATH = Path("data/diabetic_data.csv")
FIG_DIR = Path("outputs/figures")
TAB_DIR = Path("outputs/tables")
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 11})

print("1. Loading clean data for Root Cause Analysis...")
df = pd.read_csv(DATA_PATH, low_memory=False).replace('?', np.nan)
df['readmitted_binary'] = (df['readmitted'] == '<30').astype(int)
if 'weight' in df.columns:
    df = df.drop(columns=['weight'])
hospice_ids = [11, 13, 14, 19, 20, 21]
df_clean = df[~df['discharge_disposition_id'].isin(hospice_ids)].copy()

# -------------------------------------------------------------
# Function to categorize ICD-9 primary diagnosis (diag_1)
# -------------------------------------------------------------
def categorize_icd9(code):
    if pd.isna(code):
        return "Unknown/Other"
    code_str = str(code).strip()
    if code_str.startswith('V') or code_str.startswith('E'):
        return "External/Other"
    try:
        val = float(code_str)
        if 390 <= val <= 459 or val == 785:
            return "Circulatory (Tim mạch)"
        elif val == 250 or (250 <= val < 251):
            return "Diabetes (Đái tháo đường)"
        elif 460 <= val <= 519 or val == 786:
            return "Respiratory (Hô hấp)"
        elif 520 <= val <= 579 or val == 787:
            return "Digestive (Tiêu hóa)"
        elif 580 <= val <= 629 or val == 788:
            return "Genitourinary (Thận-Tiết niệu)"
        elif 140 <= val <= 239:
            return "Neoplasms (Ung bướu)"
        elif 710 <= val <= 739:
            return "Musculoskeletal (Cơ xương khớp)"
        elif 800 <= val <= 999:
            return "Injury (Chấn thương/Ngộ độc)"
        else:
            return "Other (Khác)"
    except ValueError:
        return "Unknown/Other"

df_clean['primary_diag_group'] = df_clean['diag_1'].apply(categorize_icd9)

# Diagnosis group stats
diag_stats = df_clean.groupby('primary_diag_group').agg(
    total=('encounter_id', 'count'),
    readmitted=('readmitted_binary', 'sum'),
    rate=('readmitted_binary', 'mean')
).reset_index().sort_values(by='rate', ascending=False)
diag_stats['rate_pct'] = (diag_stats['rate'] * 100).round(2)
diag_stats.to_csv(TAB_DIR / "root_cause_diagnosis_groups.csv", index=False)

plt.figure(figsize=(11, 5))
ax = sns.barplot(data=diag_stats, x='rate_pct', y='primary_diag_group', palette='mako')
plt.title("30-Day Readmission Rate by Primary Diagnosis Group", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Readmission Rate (%)", fontsize=12)
plt.ylabel("Diagnosis Group (ICD-9)", fontsize=12)
plt.axvline(df_clean['readmitted_binary'].mean() * 100, color='red', linestyle='--', label=f"Average ({df_clean['readmitted_binary'].mean()*100:.2f}%)")
for p in ax.patches:
    w = p.get_width()
    ax.annotate(f"{w:.1f}%", (w, p.get_y() + p.get_height() / 2.),
                ha='left', va='center', fontsize=10, xytext=(5, 0), textcoords='offset points')
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "root_cause_diagnosis_distribution.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# Medication Analysis (Insulin, Change, Number of Medications)
# -------------------------------------------------------------
print("2. Medication Analysis...")
insulin_stats = df_clean.groupby('insulin').agg(
    total=('encounter_id', 'count'),
    readmitted=('readmitted_binary', 'sum'),
    rate=('readmitted_binary', 'mean')
).reset_index().sort_values(by='rate', ascending=False)
insulin_stats['rate_pct'] = (insulin_stats['rate'] * 100).round(2)
insulin_stats.to_csv(TAB_DIR / "root_cause_medications.csv", index=False)

# -------------------------------------------------------------
# Statistical Modeling: Multivariate Logistic Regression for Odds Ratios
# -------------------------------------------------------------
print("3. Multivariate Logistic Regression for Odds Ratios...")
reg_df = pd.DataFrame()
reg_df['readmitted'] = df_clean['readmitted_binary']
reg_df['num_inpatient'] = df_clean['number_inpatient']
reg_df['num_emergency'] = df_clean['number_emergency']
reg_df['num_outpatient'] = df_clean['number_outpatient']
reg_df['time_in_hospital'] = df_clean['time_in_hospital']
reg_df['num_medications'] = df_clean['num_medications']
reg_df['num_procedures'] = df_clean['num_procedures']
reg_df['number_diagnoses'] = df_clean['number_diagnoses']
reg_df['is_elderly_70plus'] = df_clean['age'].isin(['[70-80)', '[80-90)', '[90-100)']).astype(int)
reg_df['insulin_down'] = (df_clean['insulin'] == 'Down').astype(int)
reg_df['insulin_up'] = (df_clean['insulin'] == 'Up').astype(int)
reg_df['insulin_steady'] = (df_clean['insulin'] == 'Steady').astype(int)
reg_df['med_changed'] = (df_clean['change'] == 'Ch').astype(int)
reg_df['no_a1c_test'] = (df_clean['A1Cresult'].isna()).astype(int)
reg_df['diabetes_med_yes'] = (df_clean['diabetesMed'] == 'Yes').astype(int)
reg_df['diag_circulatory'] = (df_clean['primary_diag_group'] == 'Circulatory (Tim mạch)').astype(int)
reg_df['diag_respiratory'] = (df_clean['primary_diag_group'] == 'Respiratory (Hô hấp)').astype(int)
reg_df['diag_diabetes'] = (df_clean['primary_diag_group'] == 'Diabetes (Đái tháo đường)').astype(int)

X_cols = [c for c in reg_df.columns if c != 'readmitted']
X = reg_df[X_cols].values
y = reg_df['readmitted'].values

# Fit logistic regression with no penalty to get unbiased MLE estimates
lr = LogisticRegression(penalty=None, solver='lbfgs', max_iter=1000)
lr.fit(X, y)

coefs = lr.coef_[0]
preds_prob = lr.predict_proba(X)[:, 1]

# Compute covariance matrix via Fisher Information (W = p * (1 - p))
W = preds_prob * (1 - preds_prob)
X_design = np.column_stack([np.ones(X.shape[0]), X])
# Subsample 20k rows for Fisher Information inversion if memory is high, or compute directly
sub_idx = np.random.choice(X.shape[0], size=min(30000, X.shape[0]), replace=False)
X_sub = X[sub_idx]
W_sub = W[sub_idx]
V = np.linalg.pinv(np.dot(X_sub.T * W_sub, X_sub)) * (X.shape[0] / len(sub_idx))
se = np.sqrt(np.diag(V))

# Exclude intercept for reporting
or_values = np.exp(coefs)
ci_lower = np.exp(coefs - 1.96 * se)
ci_upper = np.exp(coefs + 1.96 * se)
z_scores = coefs / se
p_values = 2 * (1 - stats.norm.cdf(np.abs(z_scores)))

or_df = pd.DataFrame({
    'Feature': X_cols,
    'Coefficient': coefs,
    'Odds_Ratio': or_values,
    'CI_lower': ci_lower,
    'CI_upper': ci_upper,
    'p_value': p_values
}).sort_values(by='Odds_Ratio', ascending=False)

or_df = or_df[or_df['Feature'] != 'const'].sort_values(by='Odds_Ratio', ascending=False)
or_df.to_csv(TAB_DIR / "root_cause_multivariate.csv", index=False)
print("Multivariate regression results:")
print(or_df[['Feature', 'Odds_Ratio', 'CI_lower', 'CI_upper', 'p_value']].to_string(index=False))

# Plot top odds ratios
plt.figure(figsize=(10, 6))
top_or = or_df.sort_values(by='Odds_Ratio', ascending=True)
colors = ['#d95f02' if x > 1.0 else '#1b9e77' for x in top_or['Odds_Ratio']]
plt.barh(top_or['Feature'], top_or['Odds_Ratio'] - 1.0, left=1.0, color=colors, alpha=0.85)
plt.axvline(1.0, color='black', linestyle='--', linewidth=1.2)
plt.title("Multivariate Odds Ratios for 30-Day Readmission (Logit Model)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Odds Ratio (OR)", fontsize=12)
plt.tight_layout()
plt.savefig(FIG_DIR / "root_cause_odds_ratios.png", dpi=300)
plt.close()

print("Phase 3 script finished successfully!")
