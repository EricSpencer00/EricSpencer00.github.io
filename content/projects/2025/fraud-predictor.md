---
title: "Machine Learning Fraud Identifier"
date: 2025-05-05
description: "Analyze different Machine Learning algorithms to identify fraud within a classified dataset"
tags: ["AI", "Python"]
categories: ["Projects"]
image: "/previews/"
draft: false
---

My group project for COMP 379: Machine Learning analyzed different ML algorithms for detecting fraud within a dataset that was anonymized and PCA'ed. 

https://colab.research.google.com/drive/1dP9ev-j5ZRE3_MmWzLhHxXAbEtG5qKbT?usp=sharing



## Imports

```python
import os
import subprocess

import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler

from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

from sklearn.linear_model    import LogisticRegression
from sklearn.ensemble        import RandomForestClassifier
from sklearn.svm             import SVC
from xgboost                 import XGBClassifier
from lightgbm                import LGBMClassifier
from sklearn.neighbors       import KNeighborsClassifier
```

## Download the Dataset

```python
def download_dataset():
    """Download the Kaggle creditcardfraud dataset if not present."""
    if not os.path.exists('creditcard.csv'):
        print("→ Downloading dataset via Kaggle CLI...")
        subprocess.run([
            'kaggle', 'datasets', 'download',
            '-d', 'mlg-ulb/creditcardfraud',
            '-p', '.', '--unzip'
        ], check=True)
    else:
        print("→ creditcard.csv already exists, skipping download.")

# Run the download
download_dataset()
```

## Load and Preview the Data

```python
def load_data():
    """Load the CSV into a pandas DataFrame."""
    return pd.read_csv('creditcard.csv')

# Load and preview
df = load_data()
df.head()
```

## Model Comparison Function

```python
def compare_models(df):
    # 1) Features & target
    features = [f'V{i}' for i in range(1,29)] + ['Amount', 'Time']
    X = df[features].values
    y = df['Class'].values

    # 2) Classifiers to compare
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight='balanced'),
        "RandomForest"      : RandomForestClassifier(n_estimators=100, class_weight='balanced'),
        "XGBoost"           : XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
        "LightGBM"          : LGBMClassifier(),
        "SVM (RBF)"         : SVC(kernel='rbf', probability=True, class_weight='balanced'),
        "KNN"               : KNeighborsClassifier(n_neighbors=5)
    }

    # 3) Pipeline builder
    def make_pipeline(clf):
        return Pipeline([
            ("smote",      SMOTE(random_state=42)),
            ("scaler",     StandardScaler()),
            ("classifier", clf)
        ])

    # 4) Scoring metrics
    scoring = {
        "accuracy" : "accuracy",
        "precision": "precision",
        "recall"   : "recall",
        "f1"       : "f1",
        "roc_auc"  : "roc_auc",
        "pr_auc"   : "average_precision"
    }

    # 5) Stratified 5-fold CV
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = []

    for name, clf in models.items():
        print(f"Evaluating {name}...")
        pipe = make_pipeline(clf)
        cv_res = cross_validate(pipe, X, y,
                                cv=cv, scoring=scoring,
                                return_train_score=False, n_jobs=-1)
        # Aggregate mean scores
        row = {metric: np.mean(cv_res[f"test_{metric}"]) for metric in scoring}
        row["model"] = name
        results.append(row)

    # 6) Results DataFrame
    df_res = pd.DataFrame(results).set_index("model")
    df_res = df_res.sort_values("roc_auc", ascending=False)
    return df_res
```

## Run Model Comparison

```python
# Run comparison and display results
results_df = compare_models(df)
print("=== Model Comparison Results ===")
results_df
```

### Example Output Table

| Model              | Accuracy | Precision | Recall  | F1      | ROC AUC  | PR AUC  |
|--------------------|----------|-----------|---------|---------|----------|---------|
| LogisticRegression | 0.990948 | 0.148254  | 0.89025 | 0.25403 | 0.978925 | 0.75097 |
| XGBoost            | 0.999466 | 0.850421  | 0.83944 | 0.84474 | 0.977823 | 0.85753 |
| RandomForest       | 0.999530 | 0.892663  | 0.82723 | 0.85865 | 0.968977 | 0.85102 |
| SVM (RBF)          | 0.997630 | 0.409137  | 0.82117 | 0.54560 | 0.964244 | 0.70854 |
| LightGBM           | 0.999038 | 0.684689  | 0.83129 | 0.74998 | 0.962026 | 0.81331 |
| KNN                | 0.998318 | 0.509715  | 0.81709 | 0.62733 | 0.914223 | 0.62561 |

The above Jupyter notebook was my individual contribution to the group project along with creating dataset visualizations in the [notebook report](../fraud-predictor-full)