#!/usr/bin/env python3
"""
Notebook/Script 05: SHAP Explainability for XGBoost Readmission Model
- Global explainability: Beeswarm summary plot, mean(|SHAP|) feature importance bar chart, ranking table.
- Local explainability: Waterfall plots for 3 typical patient cases (True Positive, False Positive, Low Risk).
- Strict adherence to data split: Reuses src/prep.py with random_state=42 and group split by patient_nbr.
"""

import os
import io
import re
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from xgboost import XGBClassifier
import shap
import shap.explainers._tree as tree_mod
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.prep import load_clean, feature_frame, split_by_patient

# Paths
FIG_DIR = Path("outputs/figures")
TAB_DIR = Path("outputs/tables")
FIG_DIR.mkdir(parents=True, exist_ok=True)
TAB_DIR.mkdir(parents=True, exist_ok=True)

# Set plot style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 10})

# -------------------------------------------------------------
# 0. XGBoost 3.x Compatibility Patch for SHAP TreeExplainer
# -------------------------------------------------------------
def patch_xgb_tree_loader():
    """Patches shap.explainers._tree.XGBTreeModelLoader to handle UBJSON string brackets in base_score."""
    def patched_init(self, xgb_model):
        import xgboost as xgb
        from shap.explainers._tree import decode_ubjson_buffer, _check_xgboost_version

        _check_xgboost_version(xgb.__version__)
        model = xgb_model

        raw = xgb_model.save_raw(raw_format="ubj")
        with io.BytesIO(raw) as fd:
            jmodel = decode_ubjson_buffer(fd)

        learner = jmodel["learner"]
        learner_model_param = learner["learner_model_param"]
        objective = learner["objective"]

        booster = learner["gradient_booster"]
        n_classes = max(int(learner_model_param["num_class"]), 1)
        n_targets = max(int(learner_model_param["num_target"]), 1)
        n_targets = max(n_targets, n_classes)

        if "gbtree" in booster and "model" not in booster:
            booster = booster["gbtree"]
        if booster["model"].get("iteration_indptr", None) is not None:
            iteration_indptr = np.asarray(booster["model"]["iteration_indptr"], dtype=np.int32)
            diff = np.diff(iteration_indptr)
        else:
            n_parallel_trees = int(booster["model"]["gbtree_model_param"]["num_parallel_tree"])
            diff = np.repeat(n_targets * n_parallel_trees, model.num_boosted_rounds())
        if np.any(diff != diff[0]):
            raise ValueError("vector-leaf is not yet supported.:", diff)

        self.n_trees_per_iter = int(diff[0])
        self.n_targets = n_targets
        
        # Clean XGBoost 3.x string representation of base_score
        raw_bs = learner_model_param["base_score"]
        clean_bs = float(re.sub(r'[\[\]]', '', str(raw_bs)))
        self.base_score = clean_bs
        assert self.n_trees_per_iter > 0

        self.name_obj = objective["name"]
        self.name_gbm = booster["name"]
        
        base_score = clean_bs
        import scipy.special
        if self.name_obj in ("binary:logistic", "reg:logistic"):
            self.base_score = scipy.special.logit(base_score)
        elif self.name_obj in ("reg:gamma", "reg:tweedie", "count:poisson", "survival:cox", "survival:aft"):
            self.base_score = np.log(self.base_score)
        else:
            self.base_score = base_score

        self.num_feature = int(learner_model_param["num_feature"])
        self.num_class = int(learner_model_param["num_class"])

        trees = booster["model"]["trees"]
        self.num_trees = len(trees)

        self.node_parents = []
        self.node_cleft = []
        self.node_cright = []
        self.node_sindex = []
        self.children_default = []
        self.sum_hess = []

        self.values = []
        self.thresholds = []
        self.threshold_types = []
        self.features = []
        self.split_types = []
        self.categories = []

        feature_types = model.feature_types
        if feature_types is not None:
            cat_feature_indices = np.where(np.asarray(feature_types) == "c")[0]
            self.cat_feature_indices = cat_feature_indices if len(cat_feature_indices) > 0 else None
        else:
            self.cat_feature_indices = None

        def to_integers(data):
            return np.asanyarray(data, dtype=np.uint8)

        for i in range(self.num_trees):
            tree = trees[i]
            parents = np.asarray(tree["parents"])
            self.node_parents.append(parents)
            self.node_cleft.append(np.asarray(tree["left_children"], dtype=np.int32))
            self.node_cright.append(np.asarray(tree["right_children"], dtype=np.int32))
            self.node_sindex.append(np.asarray(tree["split_indices"], dtype=np.uint32))

            base_weight = np.asarray(tree["base_weights"], dtype=np.float32)
            if base_weight.size != self.node_cleft[-1].size:
                raise ValueError("vector-leaf is not yet supported.")

            default_left = to_integers(tree["default_left"])
            default_child = np.where(default_left == 1, self.node_cleft[-1], self.node_cright[-1]).astype(np.int64)
            self.children_default.append(default_child)
            self.sum_hess.append(np.asarray(tree["sum_hessian"], dtype=np.float64))

            is_leaf = self.node_cleft[-1] == -1
            split_cond = np.asarray(tree["split_conditions"], dtype=np.float32)
            leaf_weight = np.where(is_leaf, split_cond, 0.0)
            thresholds = np.where(is_leaf, 0.0, split_cond)
            thresholds = np.where(is_leaf, 0.0, np.nextafter(thresholds, -np.float32(np.inf)))
            threshold_types = np.zeros_like(thresholds, dtype=np.int32)

            self.values.append(leaf_weight.reshape(leaf_weight.size, 1))
            self.thresholds.append(thresholds)
            self.threshold_types.append(threshold_types)

            split_idx = np.asarray(tree["split_indices"], dtype=np.int64)
            self.features.append(split_idx)

            split_types = to_integers(tree["split_type"])
            self.split_types.append(split_types)
            cat_segments = tree["categories_segments"]
            cat_sizes = tree["categories_sizes"]
            cat_nodes = tree["categories_nodes"]
            cats = tree["categories"]

            tree_categories = self.parse_categories(cat_nodes, cat_segments, cat_sizes, cats, self.node_cleft[-1])
            self.categories.append(tree_categories)

    tree_mod.XGBTreeModelLoader.__init__ = patched_init

patch_xgb_tree_loader()

# -------------------------------------------------------------
# 1. Load Data & Train Exact XGBoost Model
# -------------------------------------------------------------
print("1. Loading clean data and applying patient-level split (random_state=42)...")
df_clean = load_clean("data/diabetic_data.csv")
X, y, patients, feature_groups = feature_frame(df_clean)
X_train, X_test, y_train, y_test, train_idx, test_idx = split_by_patient(X, y, patients, test_size=0.2, random_state=42)

print(f"Train size: {X_train.shape[0]:,} rows, Test size: {X_test.shape[0]:,} rows")

print("2. Training XGBoost model with exact hyperparameters from 03_model.py...")
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

# -------------------------------------------------------------
# 2. Compute SHAP Values on Test Set
# -------------------------------------------------------------
print("3. Initializing TreeExplainer and computing SHAP values on full test set (N=19,802)...")
t0 = time.time()
explainer = shap.TreeExplainer(xgb)
shap_values_test = explainer(X_test)
print(f"SHAP values computed in {time.time() - t0:.2f}s for all 19,802 encounters.")

# Calculate global mean(|SHAP|)
mean_abs_shap = np.abs(shap_values_test.values).mean(axis=0)
imp_df = pd.DataFrame({
    'feature': X_test.columns,
    'mean_abs_shap': mean_abs_shap
}).sort_values('mean_abs_shap', ascending=False).reset_index(drop=True)
imp_df['rank'] = imp_df.index + 1

# Export global importance table
imp_df.to_csv(TAB_DIR / "shap_global_importance.csv", index=False)
print("Saved outputs/tables/shap_global_importance.csv")

print("\nTop 10 Global Features by mean(|SHAP|):")
print(imp_df.head(10).to_string())

# -------------------------------------------------------------
# 3. Global Plots: Beeswarm & Bar Importance
# -------------------------------------------------------------
print("\n4. Generating global SHAP figures...")

# Figure 1: Bar Importance (Top 15)
plt.figure(figsize=(9, 6))
top15_bar = imp_df.head(15).iloc[::-1]
plt.barh(top15_bar['feature'], top15_bar['mean_abs_shap'], color='#1e40af', edgecolor='none')
plt.xlabel("Mean Absolute SHAP Value (mean |SHAP|)")
plt.title("Top 15 Global Features by SHAP Importance (XGBoost Model)", fontsize=12, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(FIG_DIR / "shap_bar_importance.png", dpi=300)
plt.close()
print("Saved outputs/figures/shap_bar_importance.png")

# Figure 2: Summary Beeswarm Plot (Sample of 5,000 for crisp visualization)
sample_idx = X_test.sample(n=5000, random_state=42).index
sample_locs = [X_test.index.get_loc(idx) for idx in sample_idx]
shap_values_sample = shap_values_test[sample_locs]

plt.figure(figsize=(10, 7))
shap.summary_plot(shap_values_sample, X_test.iloc[sample_locs], max_display=15, show=False)
plt.title("SHAP Summary Beeswarm Plot (Top 15 Features, N=5,000 test sample)", fontsize=12, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(FIG_DIR / "shap_summary_beeswarm.png", dpi=300)
plt.close()
print("Saved outputs/figures/shap_summary_beeswarm.png")

# -------------------------------------------------------------
# 4. Local Explainability: 3 Representative Cases
# -------------------------------------------------------------
print("\n5. Generating local waterfall explanations for 3 representative clinical cases...")

# Load risk_scores.csv to align case selections
df_risk = pd.read_csv("outputs/risk_scores.csv")
df_test_full = df_clean.iloc[test_idx].copy().reset_index(drop=True)
df_test_full['prob_xgboost'] = df_risk['prob_xgboost'].values
df_test_full['risk_tier'] = df_risk['risk_tier'].values
df_test_full['readmitted_true'] = df_risk['readmitted_true'].values

# Case 1: True Positive (High Risk & Readmitted = 1) -> Encounter 174689286
# Case 2: False Positive (High Risk & Readmitted = 0) -> Encounter 109512750
# Case 3: True Negative / Low Risk (Low Risk & Readmitted = 0) -> Encounter 2913624
case_definitions = [
    {
        "case_id": 1,
        "encounter_id": 174689286,
        "label": "Case 1: True Positive (High Risk, Tái nhập thực tế = 1)",
        "file_name": "shap_case_1.png",
        "description": "Bệnh nhân trẻ tuổi [20-30), tiền sử 11 lần nhập viện trước và 9 chẩn đoán đồng mắc, liều insulin tăng. Số lần nhập viện cao đột biến đẩy log-odds rủi ro lên rất cao."
    },
    {
        "case_id": 2,
        "encounter_id": 109512750,
        "label": "Case 2: False Positive (High Risk, Tái nhập thực tế = 0)",
        "file_name": "shap_case_2.png",
        "description": "Bệnh nhân [60-70), 10 lần nhập viện trước và 9 chẩn đoán. Mô hình xếp vào High Risk do tiền sử nặng, nhưng bệnh nhân không tái nhập trong 30 ngày (False Positive vận hành)."
    },
    {
        "case_id": 3,
        "encounter_id": 2913624,
        "label": "Case 3: Low Risk / True Negative (Low Risk, Tái nhập thực tế = 0)",
        "file_name": "shap_case_3.png",
        "description": "Bệnh nhân [10-20), lần đầu nhập viện (0 lần trước), nằm viện ngắn 1 ngày, chỉ 2 chẩn đoán, không dùng insulin. Toàn bộ các yếu tố đều kéo rủi ro xuống mức đáy."
    }
]

local_records = []

for case_meta in case_definitions:
    enc_id = case_meta["encounter_id"]
    row_idx = df_test_full[df_test_full["encounter_id"] == enc_id].index[0]
    
    explanation_row = shap_values_test[row_idx]
    pred_prob = df_test_full.loc[row_idx, "prob_xgboost"]
    true_y = df_test_full.loc[row_idx, "readmitted_true"]
    risk_tier = df_test_full.loc[row_idx, "risk_tier"]
    
    # Generate waterfall plot
    plt.figure(figsize=(9, 5.5))
    shap.plots.waterfall(explanation_row, max_display=10, show=False)
    plt.title(f"{case_meta['label']}\nEncounter ID: {enc_id} | Dự báo rủi ro: {pred_prob*100:.1f}% | Nhãn thực: {true_y}", 
              fontsize=11, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(FIG_DIR / case_meta["file_name"], dpi=300)
    plt.close()
    print(f"Saved outputs/figures/{case_meta['file_name']}")
    
    # Collect top contributing features for table
    vals = explanation_row.values
    f_names = X_test.columns
    abs_vals = np.abs(vals)
    top_indices = np.argsort(abs_vals)[::-1][:6]
    
    for rank_idx, feat_idx in enumerate(top_indices, 1):
        local_records.append({
            'case_id': case_meta['case_id'],
            'case_type': case_meta['label'].split(':')[1].split('(')[0].strip(),
            'encounter_id': enc_id,
            'patient_nbr': df_test_full.loc[row_idx, "patient_nbr"],
            'age': df_test_full.loc[row_idx, "age"],
            'pred_prob': pred_prob,
            'risk_tier': risk_tier,
            'true_readmitted': true_y,
            'feature': f_names[feat_idx],
            'feature_value': explanation_row.data[feat_idx],
            'shap_value': vals[feat_idx],
            'impact_direction': 'Increases Risk' if vals[feat_idx] > 0 else 'Decreases Risk',
            'rank_in_case': rank_idx,
            'clinical_note': case_meta['description']
        })

df_local = pd.DataFrame(local_records)
df_local.to_csv(TAB_DIR / "shap_local_cases.csv", index=False)
print("Saved outputs/tables/shap_local_cases.csv")

print("\n=== SHAP Analysis Complete ===")
