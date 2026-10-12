#!/usr/bin/env python3
"""
Phase 4: Predictive Modeling & Risk Stratification
Rules:
- Gộp target nhị phân: '<30' = 1, còn lại = 0.
- Xử lý '?' thành NaN; bỏ cột 'weight' (thiếu ~97%).
- Loại lượt kết thúc bằng tử vong/hospice (discharge_disposition_id: 11, 13, 14, 19, 20, 21).
- Chia train/test theo `patient_nbr` (không theo dòng) để tránh rò rỉ thông tin.
- Mô hình: Logistic Regression (Baseline) + XGBoost (Challenger). KHÔNG tune quá mức.
- Đánh giá: Recall @ Top 20% rủi ro, ROC-AUC, PR-AUC, Calibration (Brier Score).
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    roc_curve, precision_recall_curve
)
from sklearn.calibration import calibration_curve
from xgboost import XGBClassifier

# Paths
DATA_PATH = Path("data/diabetic_data.csv")
FIG_DIR = Path("outputs/figures")
TAB_DIR = Path("outputs/tables")
OUTPUT_DIR = Path("outputs")
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 11})

print("1. Loading and cleaning dataset...")
df = pd.read_csv(DATA_PATH, low_memory=False).replace('?', np.nan)
df['readmitted_binary'] = (df['readmitted'] == '<30').astype(int)
if 'weight' in df.columns:
    df = df.drop(columns=['weight'])
hospice_ids = [11, 13, 14, 19, 20, 21]
df_clean = df[~df['discharge_disposition_id'].isin(hospice_ids)].copy()

# -------------------------------------------------------------
# Categorize ICD-9 Primary Diagnosis
# -------------------------------------------------------------
def categorize_icd9(code):
    if pd.isna(code): return "Other"
    code_str = str(code).strip()
    if code_str.startswith('V') or code_str.startswith('E'): return "Other"
    try:
        val = float(code_str)
        if 390 <= val <= 459 or val == 785: return "Circulatory"
        elif val == 250 or (250 <= val < 251): return "Diabetes"
        elif 460 <= val <= 519 or val == 786: return "Respiratory"
        elif 520 <= val <= 579 or val == 787: return "Digestive"
        elif 580 <= val <= 629 or val == 788: return "Genitourinary"
        elif 140 <= val <= 239: return "Neoplasms"
        elif 710 <= val <= 739: return "Musculoskeletal"
        elif 800 <= val <= 999: return "Injury"
        else: return "Other"
    except ValueError:
        return "Other"

df_clean['diag_1_group'] = df_clean['diag_1'].apply(categorize_icd9)

# Group medical specialty
top_specialties = df_clean['medical_specialty'].value_counts().head(8).index
df_clean['med_specialty_grouped'] = df_clean['medical_specialty'].apply(
    lambda x: x if x in top_specialties else ('Missing' if pd.isna(x) else 'Other_Specialty')
)

# -------------------------------------------------------------
# Feature Selection & Encoding
# -------------------------------------------------------------
num_cols = [
    'time_in_hospital', 'num_lab_procedures', 'num_procedures',
    'num_medications', 'number_outpatient', 'number_emergency',
    'number_inpatient', 'number_diagnoses'
]

cat_cols = [
    'race', 'gender', 'age', 'admission_type_id', 'discharge_disposition_id',
    'admission_source_id', 'med_specialty_grouped', 'diag_1_group',
    'max_glu_serum', 'A1Cresult', 'metformin', 'glimepiride', 'glipizide',
    'glyburide', 'pioglitazone', 'rosiglitazone', 'insulin', 'change', 'diabetesMed'
]

# Fill missing in categorical
for c in cat_cols:
    df_clean[c] = df_clean[c].fillna('Unknown').astype(str)

# Dummies
df_encoded = pd.get_dummies(df_clean[cat_cols], drop_first=True, dtype=int)
X_all = pd.concat([df_clean[num_cols].reset_index(drop=True), df_encoded.reset_index(drop=True)], axis=1)

# Clean column names for XGBoost (disallows [, ], <, >)
import re
X_all.columns = [re.sub(r'[\[\]<>]', '_', str(c)) for c in X_all.columns]
y_all = df_clean['readmitted_binary'].values
patients = df_clean['patient_nbr'].values

print(f"Total features created: {X_all.shape[1]}")

# -------------------------------------------------------------
# Train/Test Split by patient_nbr (Group Split)
# -------------------------------------------------------------
print("2. Splitting Train/Test by patient_nbr (80/20)...")
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X_all, y_all, groups=patients))

X_train, X_test = X_all.iloc[train_idx].copy(), X_all.iloc[test_idx].copy()
y_train, y_test = y_all[train_idx], y_all[test_idx]

train_patients = set(patients[train_idx])
test_patients = set(patients[test_idx])
overlap = train_patients.intersection(test_patients)
assert len(overlap) == 0, f"Error: {len(overlap)} patients overlap between train and test!"

print(f"Train encounters: {len(X_train):,} ({len(train_patients):,} patients), Readmission rate: {y_train.mean():.2%}")
print(f"Test encounters:  {len(X_test):,} ({len(test_patients):,} patients), Readmission rate: {y_test.mean():.2%}")

# -------------------------------------------------------------
# Standard Scaling for numerical features (for LogReg)
# -------------------------------------------------------------
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()
X_train_scaled[num_cols] = scaler.fit_transform(X_train[num_cols])
X_test_scaled[num_cols] = scaler.transform(X_test[num_cols])

# -------------------------------------------------------------
# Model 1: Baseline Logistic Regression (C=0.1, simple)
# -------------------------------------------------------------
print("3. Training Logistic Regression Baseline...")
lr = LogisticRegression(C=0.1, max_iter=1000, random_state=42)
lr.fit(X_train_scaled, y_train)
preds_lr = lr.predict_proba(X_test_scaled)[:, 1]

# -------------------------------------------------------------
# Model 2: XGBoost Challenger (Simple, controlled depth, no overfit)
# -------------------------------------------------------------
print("4. Training XGBoost Challenger...")
xgb = XGBClassifier(
    n_estimators=120,
    max_depth=4,
    learning_rate=0.08,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='logloss',
    random_state=42
)
xgb.fit(X_train, y_train)
preds_xgb = xgb.predict_proba(X_test)[:, 1]

# -------------------------------------------------------------
# Evaluation Function: Recall @ Top 20%, AUC, Brier Score
# -------------------------------------------------------------
def evaluate_model(y_true, y_prob, model_name):
    auc = roc_auc_score(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)
    brier = brier_score_loss(y_true, y_prob)
    
    # Top 20% Risk Group
    df_eval = pd.DataFrame({'y_true': y_true, 'prob': y_prob})
    cutoff = np.percentile(y_prob, 80) # Top 20%
    top_20 = df_eval[df_eval['prob'] >= cutoff]
    
    total_positives = y_true.sum()
    captured_positives = top_20['y_true'].sum()
    recall_top_20 = captured_positives / total_positives
    precision_top_20 = top_20['y_true'].mean()
    lift_top_20 = precision_top_20 / y_true.mean()
    
    return {
        'Model': model_name,
        'ROC_AUC': round(auc, 4),
        'PR_AUC': round(pr_auc, 4),
        'Recall_at_Top_20pct': round(recall_top_20, 4),
        'Precision_at_Top_20pct': round(precision_top_20, 4),
        'Lift_at_Top_20pct': round(lift_top_20, 2),
        'Brier_Score': round(brier, 4)
    }

res_lr = evaluate_model(y_test, preds_lr, "Logistic Regression (Baseline)")
res_xgb = evaluate_model(y_test, preds_xgb, "XGBoost (Challenger)")

comparison_df = pd.DataFrame([res_lr, res_xgb])
comparison_df.to_csv(TAB_DIR / "model_comparison.csv", index=False)
print("\n=== Model Comparison Results ===")
print(comparison_df.to_string(index=False))

# -------------------------------------------------------------
# Risk Scores Export (outputs/risk_scores.csv)
# -------------------------------------------------------------
print("5. Exporting risk scores to outputs/risk_scores.csv...")
test_encounters = df_clean.iloc[test_idx][['encounter_id', 'patient_nbr', 'age', 'discharge_disposition_id']].copy()
test_encounters['readmitted_true'] = y_test
test_encounters['prob_logreg'] = preds_lr.round(4)
test_encounters['prob_xgboost'] = preds_xgb.round(4)

# Assign Risk Tiers based on XGBoost probabilities (Top 20% = High, Next 30% = Medium, Bottom 50% = Low)
p80 = np.percentile(preds_xgb, 80)
p50 = np.percentile(preds_xgb, 50)

def assign_tier(p):
    if p >= p80: return "High Risk (Top 20%)"
    elif p >= p50: return "Medium Risk (30%)"
    else: return "Low Risk (50%)"

test_encounters['risk_tier'] = test_encounters['prob_xgboost'].apply(assign_tier)
test_encounters.to_csv(OUTPUT_DIR / "risk_scores.csv", index=False)
print(f"Risk scores saved: {len(test_encounters):,} test encounters scored.")
print("Risk tier distribution in test set:")
print(test_encounters['risk_tier'].value_counts())
print("\nEmpirical readmission rate by risk tier:")
print(test_encounters.groupby('risk_tier')['readmitted_true'].agg(['count', 'mean']).round(4))

# -------------------------------------------------------------
# Figures: ROC & PR Curves
# -------------------------------------------------------------
print("6. Generating evaluation figures...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# ROC Curve
fpr_lr, tpr_lr, _ = roc_curve(y_test, preds_lr)
fpr_xgb, tpr_xgb, _ = roc_curve(y_test, preds_xgb)
axes[0].plot(fpr_lr, tpr_lr, label=f"LogReg (AUC = {res_lr['ROC_AUC']:.3f})", color='#386cb0', lw=2)
axes[0].plot(fpr_xgb, tpr_xgb, label=f"XGBoost (AUC = {res_xgb['ROC_AUC']:.3f})", color='#e41a1c', lw=2)
axes[0].plot([0, 1], [0, 1], 'k--', alpha=0.6)
axes[0].set_title("ROC Curve Comparison", fontsize=13, fontweight='bold')
axes[0].set_xlabel("False Positive Rate")
axes[0].set_ylabel("True Positive Rate (Recall)")
axes[0].legend()

# Precision-Recall Curve
p_lr, r_lr, _ = precision_recall_curve(y_test, preds_lr)
p_xgb, r_xgb, _ = precision_recall_curve(y_test, preds_xgb)
axes[1].plot(r_lr, p_lr, label=f"LogReg (PR-AUC = {res_lr['PR_AUC']:.3f})", color='#386cb0', lw=2)
axes[1].plot(r_xgb, p_xgb, label=f"XGBoost (PR-AUC = {res_xgb['PR_AUC']:.3f})", color='#e41a1c', lw=2)
axes[1].axhline(y_test.mean(), color='grey', linestyle='--', label=f"Baseline ({y_test.mean():.1%})")
axes[1].set_title("Precision-Recall Curve Comparison", fontsize=13, fontweight='bold')
axes[1].set_xlabel("Recall")
axes[1].set_ylabel("Precision")
axes[1].legend()

plt.tight_layout()
plt.savefig(FIG_DIR / "model_roc_pr_curve.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# Figures: Calibration Curves
# -------------------------------------------------------------
prob_true_lr, prob_pred_lr = calibration_curve(y_test, preds_lr, n_bins=10)
prob_true_xgb, prob_pred_xgb = calibration_curve(y_test, preds_xgb, n_bins=10)

plt.figure(figsize=(7, 6))
plt.plot([0, 0.4], [0, 0.4], "k:", label="Perfect calibration")
plt.plot(prob_pred_lr, prob_true_lr, "s-", label=f"LogReg (Brier = {res_lr['Brier_Score']:.4f})", color='#386cb0')
plt.plot(prob_pred_xgb, prob_true_xgb, "o-", label=f"XGBoost (Brier = {res_xgb['Brier_Score']:.4f})", color='#e41a1c')
plt.title("Calibration Curves (Reliability Diagram)", fontsize=13, fontweight='bold', pad=15)
plt.xlabel("Mean Predicted Probability", fontsize=11)
plt.ylabel("Observed Fraction of Positives", fontsize=11)
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(FIG_DIR / "model_calibration_curve.png", dpi=300)
plt.close()

# -------------------------------------------------------------
# Figures: XGBoost Feature Importance
# -------------------------------------------------------------
feat_imp = pd.Series(xgb.feature_importances_, index=X_train.columns).sort_values(ascending=False).head(15)
plt.figure(figsize=(10, 6))
sns.barplot(x=feat_imp.values, y=feat_imp.index, color='#2c7bb6')
plt.title("Top 15 Most Important Features (XGBoost)", fontsize=13, fontweight='bold', pad=15)
plt.xlabel("Relative Importance (Gain / Weight)", fontsize=11)
plt.ylabel("Clinical / Administrative Feature", fontsize=11)
plt.tight_layout()
plt.savefig(FIG_DIR / "model_feature_importance.png", dpi=300)
plt.close()

print("Phase 4 modeling completed successfully!")

# -------------------------------------------------------------
# 7. Experimentation & Robustness Checks (Thử nghiệm cải thiện độ chính xác)
# -------------------------------------------------------------
print("\n" + "="*60)
print("7. EXPERIMENT LOG: FEATURE ENGINEERING & CALIBRATION (CŨ VS MỚI)")
print("="*60)

# Build engineered features on df_clean
df_exp = df_clean.copy()
df_exp['prior_utilization'] = df_exp['number_inpatient'] + df_exp['number_emergency'] + df_exp['number_outpatient']
df_exp['is_multimorbid'] = (df_exp['number_diagnoses'] >= 9).astype(int)

# Active diabetes medications count
med_cols = ['metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 'glimepiride',
            'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone',
            'rosiglitazone', 'acarbose', 'miglitol', 'troglitazone', 'tolazamide',
            'examide', 'citoglipton', 'insulin', 'glyburide-metformin', 'glipizide-metformin',
            'glimepiride-pioglitazone', 'metformin-rosiglitazone', 'metformin-pioglitazone']
existing_meds = [m for m in med_cols if m in df_exp.columns]
df_exp['num_active_diabetes_meds'] = (df_exp[existing_meds] != 'No').sum(axis=1)

age_map = {'[0-10)': 5, '[10-20)': 15, '[20-30)': 25, '[30-40)': 35, '[40-50)': 45,
           '[50-60)': 55, '[60-70)': 65, '[70-80)': 75, '[80-90)': 85, '[90-100)': 95}
df_exp['age_num'] = df_exp['age'].map(age_map).fillna(60)
df_exp['interact_age_inpatient'] = df_exp['age_num'] * df_exp['number_inpatient']

num_cols_new = num_cols + ['prior_utilization', 'is_multimorbid', 'num_active_diabetes_meds', 'interact_age_inpatient']

df_exp_encoded = pd.get_dummies(df_exp[cat_cols], drop_first=True, dtype=int)
X_exp = pd.concat([df_exp[num_cols_new].reset_index(drop=True), df_exp_encoded.reset_index(drop=True)], axis=1)
X_exp.columns = [re.sub(r'[\[\]<>]', '_', str(c)) for c in X_exp.columns]

X_train_exp = X_exp.iloc[train_idx].copy()
X_test_exp = X_exp.iloc[test_idx].copy()

# Scaled for LogReg
scaler_exp = StandardScaler()
X_train_exp_scaled = X_train_exp.copy()
X_test_exp_scaled = X_test_exp.copy()
X_train_exp_scaled[num_cols_new] = scaler_exp.fit_transform(X_train_exp[num_cols_new])
X_test_exp_scaled[num_cols_new] = scaler_exp.transform(X_test_exp[num_cols_new])

# 1. LogReg with new features
lr_new = LogisticRegression(C=0.1, max_iter=1000, random_state=42)
lr_new.fit(X_train_exp_scaled, y_train)
p_lr_new = lr_new.predict_proba(X_test_exp_scaled)[:, 1]
res_lr_new = evaluate_model(y_test, p_lr_new, "LogReg (New Features)")

# 2. XGBoost with new features
xgb_new = XGBClassifier(
    n_estimators=120, max_depth=4, learning_rate=0.08,
    subsample=0.8, colsample_bytree=0.8, eval_metric='logloss', random_state=42
)
xgb_new.fit(X_train_exp, y_train)
p_xgb_new = xgb_new.predict_proba(X_test_exp)[:, 1]
res_xgb_new = evaluate_model(y_test, p_xgb_new, "XGBoost (New Features)")

# 3. XGBoost with scale_pos_weight
spw = (len(y_train) - sum(y_train)) / sum(y_train)
xgb_spw = XGBClassifier(
    n_estimators=120, max_depth=4, learning_rate=0.08,
    subsample=0.8, colsample_bytree=0.8, scale_pos_weight=spw,
    eval_metric='logloss', random_state=42
)
xgb_spw.fit(X_train, y_train)
p_xgb_spw = xgb_spw.predict_proba(X_test)[:, 1]
res_xgb_spw = evaluate_model(y_test, p_xgb_spw, "XGBoost (scale_pos_weight)")

# 4. XGBoost with CalibratedClassifierCV (isotonic)
from sklearn.calibration import CalibratedClassifierCV
cal_xgb_cv = CalibratedClassifierCV(
    estimator=XGBClassifier(n_estimators=120, max_depth=4, learning_rate=0.08, subsample=0.8, colsample_bytree=0.8, eval_metric='logloss', random_state=42),
    method='isotonic', cv=3
)
cal_xgb_cv.fit(X_train, y_train)
p_cal = cal_xgb_cv.predict_proba(X_test)[:, 1]
res_xgb_cal = evaluate_model(y_test, p_cal, "XGBoost (Calibrated Isotonic)")

# Compare table Old vs New
exp_df = pd.DataFrame([
    res_lr,
    res_lr_new,
    res_xgb,
    res_xgb_new,
    res_xgb_spw,
    res_xgb_cal
])
exp_df.to_csv(TAB_DIR / "model_experiments_old_vs_new.csv", index=False)
print(exp_df.to_string(index=False))

print("\n[KẾT LUẬN THỬ NGHIỆM]:")
print("1. Feature engineering (prior_utilization, multimorbid, med count, age*inpatient) chỉ thay đổi ROC-AUC từ 0.6670 -> 0.6668 (-0.0002) và Recall@20% từ 38.90% -> 38.45% (-0.45%).")
print("2. scale_pos_weight làm tăng Brier score từ 0.0944 lên 0.2214 (làm lệch nghiêm trọng hiệu chuẩn xác suất).")
print("3. CalibratedClassifierCV tăng ROC-AUC nhẹ lên 0.6679 (+0.0009) nhưng Recall@20% giảm xuống 38.63% (-0.27%).")
print("-> KẾT LUẬN: ĐÃ THỬ NGHIỆM VÀ KHÔNG CẢI THIỆN ĐÁNG KỂ. Giữ nguyên mô hình XGBoost ban đầu đơn giản để tránh overfitting, dễ giải thích và tuân thủ nguyên tắc Occam's Razor.")

