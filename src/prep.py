#!/usr/bin/env python3
"""
Data preprocessing, feature engineering, and patient-level splitting module.
Reused across modeling and analysis to ensure zero data leakage.
"""

import re
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit


def categorize_icd9(code):
    """Categorizes primary ICD-9 diagnosis into major clinical disease groups."""
    if pd.isna(code):
        return "Other"
    code_str = str(code).strip()
    if code_str.startswith('V') or code_str.startswith('E'):
        return "Other"
    try:
        val = float(code_str)
        if 390 <= val <= 459 or val == 785:
            return "Circulatory"
        elif val == 250 or (250 <= val < 251):
            return "Diabetes"
        elif 460 <= val <= 519 or val == 786:
            return "Respiratory"
        elif 520 <= val <= 579 or val == 787:
            return "Digestive"
        elif 580 <= val <= 629 or val == 788:
            return "Genitourinary"
        elif 140 <= val <= 239:
            return "Neoplasms"
        elif 710 <= val <= 739:
            return "Musculoskeletal"
        elif 800 <= val <= 999:
            return "Injury"
        else:
            return "Other"
    except ValueError:
        return "Other"


def load_clean(data_path="data/diabetic_data.csv"):
    """
    Loads raw CSV and applies project rules:
    - Replaces '?' with NaN
    - Binary target: '<30' -> 1, others -> 0
    - Drops 'weight'
    - Filters out hospice/deceased disposition IDs (11, 13, 14, 19, 20, 21)
    - Groups ICD-9 primary diagnosis and medical specialties
    """
    path = Path(data_path)
    df = pd.read_csv(path, low_memory=False).replace('?', np.nan)
    
    # Rule: Binary target
    df['readmitted_binary'] = (df['readmitted'] == '<30').astype(int)
    
    # Rule: Drop weight
    if 'weight' in df.columns:
        df = df.drop(columns=['weight'])
        
    # Rule: Filter hospice/deceased
    hospice_ids = [11, 13, 14, 19, 20, 21]
    df_clean = df[~df['discharge_disposition_id'].isin(hospice_ids)].copy()
    
    # Clinical grouping
    df_clean['diag_1_group'] = df_clean['diag_1'].apply(categorize_icd9)
    top_specialties = df_clean['medical_specialty'].value_counts().head(8).index
    df_clean['med_specialty_grouped'] = df_clean['medical_specialty'].apply(
        lambda x: x if x in top_specialties else ('Missing' if pd.isna(x) else 'Other_Specialty')
    )
    
    return df_clean


def feature_frame(df_clean):
    """
    Builds feature matrix X, target y, patient array, and feature group dictionary.
    Columns are sanitized to disallow [, ], <, > for XGBoost compatibility.
    """
    raw_feature_groups = {
        'demographics': ['race', 'gender', 'age'],
        'prior_utilization': ['number_inpatient', 'number_emergency', 'number_outpatient'],
        'diagnoses': ['diag_1_group', 'number_diagnoses'],
        'medications': [
            'metformin', 'glimepiride', 'glipizide', 'glyburide',
            'pioglitazone', 'rosiglitazone', 'insulin', 'change', 'diabetesMed'
        ],
        'labs': ['A1Cresult', 'max_glu_serum'],
        'admission_los': [
            'admission_type_id', 'discharge_disposition_id', 'admission_source_id',
            'med_specialty_grouped', 'time_in_hospital', 'num_lab_procedures',
            'num_procedures', 'num_medications'
        ]
    }
    
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
    
    df_proc = df_clean.copy()
    for c in cat_cols:
        df_proc[c] = df_proc[c].fillna('Unknown').astype(str)
        
    df_encoded = pd.get_dummies(df_proc[cat_cols], drop_first=True, dtype=int)
    X = pd.concat([df_proc[num_cols].reset_index(drop=True), df_encoded.reset_index(drop=True)], axis=1)
    
    # Sanitize column names
    clean_cols = [re.sub(r'[\[\]<>]', '_', str(c)) for c in X.columns]
    X.columns = clean_cols
    
    y = df_proc['readmitted_binary'].values
    patients = df_proc['patient_nbr'].values
    
    # Map encoded column names back to feature groups
    encoded_feature_groups = {}
    for group_name, raw_cols in raw_feature_groups.items():
        matched_cols = []
        for raw_c in raw_cols:
            if raw_c in num_cols:
                if raw_c in X.columns:
                    matched_cols.append(raw_c)
            else:
                prefix = f"{raw_c}_"
                matched_cols.extend([col for col in X.columns if col.startswith(prefix)])
        encoded_feature_groups[group_name] = matched_cols
        
    return X, y, patients, encoded_feature_groups


def split_by_patient(X, y, patients, test_size=0.2, random_state=42):
    """
    Splits data into train and test sets by patient_nbr to avoid data leakage.
    Ensures zero overlapping patients between train and test.
    """
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    train_idx, test_idx = next(gss.split(X, y, groups=patients))
    
    train_patients = set(patients[train_idx])
    test_patients = set(patients[test_idx])
    assert len(train_patients.intersection(test_patients)) == 0, "Data leakage detected: overlapping patients!"
    
    X_train = X.iloc[train_idx].copy()
    X_test = X.iloc[test_idx].copy()
    y_train = y[train_idx]
    y_test = y[test_idx]
    
    return X_train, X_test, y_train, y_test, train_idx, test_idx
