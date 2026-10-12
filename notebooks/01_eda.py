#!/usr/bin/env python3
"""
Phase 2: EDA & Data Preprocessing
Rules:
- Gộp target nhị phân: '<30' = 1, còn lại = 0.
- Xử lý '?' thành NaN; bỏ cột 'weight' (thiếu ~97%).
- Loại lượt kết thúc bằng tử vong/hospice (discharge_disposition_id: 11, 13, 14, 19, 20, 21).
- Phân tích tỷ lệ tái nhập viện theo tuổi, khoa, số lần khám trước, thuốc và thời gian nằm viện.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
DATA_PATH = Path("data/diabetic_data.csv")
FIG_DIR = Path("outputs/figures")
TAB_DIR = Path("outputs/tables")
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)

# Set style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 11})

print("1. Loading raw data...")
df = pd.read_csv(DATA_PATH, low_memory=False)
raw_rows, raw_cols = df.shape
print(f"Raw data: {raw_rows:,} rows, {raw_cols} columns")

# Rule 1: Replace '?' with NaN
df = df.replace('?', np.nan)

# Rule 2: Binary target: '<30' -> 1, others -> 0
df['readmitted_binary'] = (df['readmitted'] == '<30').astype(int)

# Rule 3: Drop 'weight' (missing ~97%)
if 'weight' in df.columns:
    df = df.drop(columns=['weight'])

# Rule 4: Exclude discharge to hospice/death (11, 13, 14, 19, 20, 21)
hospice_ids = [11, 13, 14, 19, 20, 21]
excluded_count = df['discharge_disposition_id'].isin(hospice_ids).sum()
df_clean = df[~df['discharge_disposition_id'].isin(hospice_ids)].copy()

clean_rows, clean_cols = df_clean.shape
print(f"Excluded {excluded_count:,} deceased/hospice encounters.")
print(f"Clean data: {clean_rows:,} rows, {clean_cols} columns")
print(f"Target readmitted (<30 days) count: {df_clean['readmitted_binary'].sum():,} ({df_clean['readmitted_binary'].mean():.2%})")

# Save overall summary table
overall_summary = pd.DataFrame({
    'Metric': [
        'Total raw encounters',
        'Excluded deceased/hospice',
        'Clean encounters analyzed',
        'Unique patients',
        'Readmitted within 30 days (Target=1)',
        '30-day Readmission Rate (%)'
    ],
    'Value': [
        f"{raw_rows:,}",
        f"{excluded_count:,}",
        f"{clean_rows:,}",
        f"{df_clean['patient_nbr'].nunique():,}",
        f"{df_clean['readmitted_binary'].sum():,}",
        f"{df_clean['readmitted_binary'].mean()*100:.2f}%"
    ]
})
overall_summary.to_csv(TAB_DIR / "eda_summary_overall.csv", index=False)

# -------------------------------------------------------------
# EDA 1: Readmission by Age Bracket
# -------------------------------------------------------------
print("2. Analyzing Readmission by Age...")
age_order = ['[0-10)', '[10-20)', '[20-30)', '[30-40)', '[40-50)', '[50-60)', '[60-70)', '[70-80)', '[80-90)', '[90-100)']
age_df = df_clean.groupby('age').agg(
    total_encounters=('encounter_id', 'count'),
    readmitted_count=('readmitted_binary', 'sum'),
    readmission_rate=('readmitted_binary', 'mean')
).reindex(age_order).reset_index()
age_df['readmission_rate_pct'] = (age_df['readmission_rate'] * 100).round(2)
age_df.to_csv(TAB_DIR / "eda_readmission_by_age.csv", index=False)

plt.figure(figsize=(10, 5))
ax = sns.barplot(data=age_df, x='age', y='readmission_rate_pct', color='#2b5c8f')
plt.title("30-Day Readmission Rate by Age Group", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Age Bracket", fontsize=12)
plt.ylabel("Readmission Rate (%)", fontsize=12)
plt.axhline(df_clean['readmitted_binary'].mean() * 100, color='red', linestyle='--', label=f"Average ({df_clean['readmitted_binary'].mean()*100:.2f}%)")
for p in ax.patches:
    h = p.get_height()
    if h > 0:
        ax.annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h),
                    ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_readmission_by_age.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# EDA 2: Readmission by Medical Specialty (Top 10 specialties)
# -------------------------------------------------------------
print("3. Analyzing Readmission by Medical Specialty...")
specialty_df = df_clean.copy()
specialty_df['medical_specialty'] = specialty_df['medical_specialty'].fillna('Missing / Unknown')
top_specialties = specialty_df['medical_specialty'].value_counts().head(10).index

spec_stats = specialty_df[specialty_df['medical_specialty'].isin(top_specialties)].groupby('medical_specialty').agg(
    total_encounters=('encounter_id', 'count'),
    readmitted_count=('readmitted_binary', 'sum'),
    readmission_rate=('readmitted_binary', 'mean')
).reset_index().sort_values(by='readmission_rate', ascending=False)
spec_stats['readmission_rate_pct'] = (spec_stats['readmission_rate'] * 100).round(2)
spec_stats.to_csv(TAB_DIR / "eda_readmission_by_specialty.csv", index=False)

plt.figure(figsize=(12, 6))
ax = sns.barplot(data=spec_stats, x='readmission_rate_pct', y='medical_specialty', palette='Blues_r')
plt.title("30-Day Readmission Rate by Top 10 Medical Specialties", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Readmission Rate (%)", fontsize=12)
plt.ylabel("Medical Specialty", fontsize=12)
plt.axvline(df_clean['readmitted_binary'].mean() * 100, color='red', linestyle='--', label=f"Average ({df_clean['readmitted_binary'].mean()*100:.2f}%)")
for p in ax.patches:
    w = p.get_width()
    ax.annotate(f"{w:.1f}%", (w, p.get_y() + p.get_height() / 2.),
                ha='left', va='center', fontsize=10, xytext=(5, 0), textcoords='offset points')
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_readmission_by_specialty.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# EDA 3: Readmission by Prior Utilization (Prior Inpatient Visits)
# -------------------------------------------------------------
print("4. Analyzing Readmission by Prior Utilization...")
df_clean['prior_inpatient_group'] = df_clean['number_inpatient'].apply(
    lambda x: '0' if x == 0 else ('1' if x == 1 else ('2-3' if x in [2, 3] else '4+'))
)
inpatient_order = ['0', '1', '2-3', '4+']
inp_stats = df_clean.groupby('prior_inpatient_group').agg(
    total_encounters=('encounter_id', 'count'),
    readmitted_count=('readmitted_binary', 'sum'),
    readmission_rate=('readmitted_binary', 'mean')
).reindex(inpatient_order).reset_index()
inp_stats['readmission_rate_pct'] = (inp_stats['readmission_rate'] * 100).round(2)
inp_stats.to_csv(TAB_DIR / "eda_readmission_by_prior_utilization.csv", index=False)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
# Plot A: Prior Inpatient
sns.barplot(data=inp_stats, x='prior_inpatient_group', y='readmission_rate_pct', color='#d95f02', ax=axes[0])
axes[0].set_title("Readmission Rate by Prior Inpatient Admissions (Year Prior)", fontsize=13, fontweight='bold')
axes[0].set_xlabel("Number of Prior Inpatient Admissions", fontsize=11)
axes[0].set_ylabel("Readmission Rate (%)", fontsize=11)
axes[0].axhline(df_clean['readmitted_binary'].mean() * 100, color='grey', linestyle='--')
for p in axes[0].patches:
    h = p.get_height()
    axes[0].annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h),
                     ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')

# Plot B: Prior Emergency Visits
df_clean['prior_er_group'] = df_clean['number_emergency'].apply(
    lambda x: '0' if x == 0 else ('1' if x == 1 else ('2+' if x >= 2 else str(x)))
)
er_order = ['0', '1', '2+']
er_stats = df_clean.groupby('prior_er_group').agg(
    total_encounters=('encounter_id', 'count'),
    readmitted_count=('readmitted_binary', 'sum'),
    readmission_rate=('readmitted_binary', 'mean')
).reindex(er_order).reset_index()
er_stats['readmission_rate_pct'] = (er_stats['readmission_rate'] * 100).round(2)

sns.barplot(data=er_stats, x='prior_er_group', y='readmission_rate_pct', color='#7570b3', ax=axes[1])
axes[1].set_title("Readmission Rate by Prior Emergency Visits (Year Prior)", fontsize=13, fontweight='bold')
axes[1].set_xlabel("Number of Prior Emergency Visits", fontsize=11)
axes[1].set_ylabel("Readmission Rate (%)", fontsize=11)
axes[1].axhline(df_clean['readmitted_binary'].mean() * 100, color='grey', linestyle='--')
for p in axes[1].patches:
    h = p.get_height()
    axes[1].annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h),
                     ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')

plt.tight_layout()
plt.savefig(FIG_DIR / "eda_readmission_by_prior_visits.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# EDA 4: Clinical testing & Medication changes (A1C & Med Change)
# -------------------------------------------------------------
print("5. Analyzing Clinical Testing & Medication Changes...")
a1c_stats = df_clean.groupby(['A1Cresult', 'change']).agg(
    total=('encounter_id', 'count'),
    readmitted=('readmitted_binary', 'sum'),
    rate=('readmitted_binary', 'mean')
).reset_index()
a1c_stats['rate_pct'] = (a1c_stats['rate'] * 100).round(2)
a1c_stats.to_csv(TAB_DIR / "eda_readmission_by_a1c_and_change.csv", index=False)

plt.figure(figsize=(10, 5))
ax = sns.barplot(data=a1c_stats, x='A1Cresult', y='rate_pct', hue='change', palette='Set2')
plt.title("Readmission Rate by HbA1c Result and Medication Change", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("HbA1c Test Result during Encounter", fontsize=12)
plt.ylabel("Readmission Rate (%)", fontsize=12)
plt.legend(title="Medication Changed (Ch/No)")
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_readmission_by_a1c.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# EDA 5: Length of Stay & Number of Diagnoses
# -------------------------------------------------------------
print("6. Analyzing Length of Stay and Diagnoses...")
stay_stats = df_clean.groupby('time_in_hospital').agg(
    total=('encounter_id', 'count'),
    readmitted=('readmitted_binary', 'sum'),
    rate=('readmitted_binary', 'mean')
).reset_index()
stay_stats['rate_pct'] = (stay_stats['rate'] * 100).round(2)

plt.figure(figsize=(11, 5))
plt.plot(stay_stats['time_in_hospital'], stay_stats['rate_pct'], marker='o', color='#e7298a', linewidth=2.5)
plt.title("30-Day Readmission Rate by Length of Stay (Days in Hospital)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Length of Stay (Days)", fontsize=12)
plt.ylabel("Readmission Rate (%)", fontsize=12)
plt.axhline(df_clean['readmitted_binary'].mean() * 100, color='grey', linestyle='--', label="Average")
plt.xticks(range(1, 15))
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "eda_readmission_by_stay_and_meds.png", dpi=300)
plt.close()

print("EDA completed successfully! Figures and tables saved.")
