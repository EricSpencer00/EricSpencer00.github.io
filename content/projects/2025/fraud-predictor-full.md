---
draft: true
---

## Credit Card Fraud Detection Project - COMP 379/479 Machine Learning
Ololade Akinsanola, Oliver Schramm, Eric Spencer, Tigist Tefera, and Avery Walker# Data Download


---

### [#1]


```
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os
from imblearn.over_sampling import SMOTE
from collections import Counter
import xgboost
```


---

### [#2]


```
# 1. Install Kaggle CLI
!pip install kaggle

# 2. Write your credentials to ~/.kaggle/kaggle.json
import os, json

# Ensure the directory exists
os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)

creds = {
    "username": "ericspencer00",
    "key": "xxxxxxxxxxxxxxxxx"
}

# Write and secure the file
with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
    json.dump(creds, f)
os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)

# 3. Point Kaggle CLI at that folder
os.environ["KAGGLE_CONFIG_DIR"] = os.path.expanduser("~/.kaggle")

# 4. Download & unzip the dataset
!kaggle datasets download -d mlg-ulb/creditcardfraud -p . --unzip

# 5. Load into pandas
import pandas as pd
data = pd.read_csv("creditcard.csv")
print("Data downloaded successfully.")
print(data.head())

```
Output:
## Basic Info + Data Visualizations


---

### [#3]


```
print(data.info())
print(data.head())
# Check the class distribution
print(data["Class"].value_counts())  # 0 = Non-fraud, 1 = Fraud
```
Output:
Basic info:
- There are some null values we account for later
- SMOTE will be useful for classification
- V1-V28 are anonymized PCA components, we can use feature importance to see which ones matter most

---

### [#4]


```
sns.countplot(x='Class', data=data)
print(data["Class"].value_counts())
plt.title("Fraud vs Non-Fraud Distribution")
plt.show()
```
Output:


---

### [#5]


```
sns.boxplot(x='Class', y='Amount', data=data)
plt.title("Transaction Amount by Fraud Class")
plt.show()
```
Output:
This shows we can potentially eliminate any classifications for fraud past ~2000 transactions

---

### [#6]


```
# Create a heatmap to visualize the distribution
plt.figure(figsize=(10, 6))
sns.heatmap(pd.crosstab(data['Class'], pd.cut(data['Amount'], bins=10)), annot=True, fmt='d', cmap='Blues')
plt.title('Distribution of Fraud vs. Non-Fraud by Transaction Amount')
plt.xlabel('Transaction Amount Bins')
plt.ylabel('Fraud Class (0: Non-Fraud, 1: Fraud)')
plt.show()
```
Output:
Distribution of transaction amount

---

### [#7]


```
plt.figure(figsize=(10,5))
sns.histplot(data["Amount"], bins=50, kde=True)
plt.title("Distribution of Transaction Amounts")
plt.xlabel("Transaction Amount ($)")
plt.ylabel("Frequency")
plt.show()
```
Output:
A majority of the transactions are very low (close to zero)
There are very few high-value transactions.
Fraudulent transactions usually involve very high-values or unusual amounts of purchases.Features Correlation plot

---

### [#8]


```
plt.figure(figsize=(12,6))
sns.heatmap(data.corr(), cmap="coolwarm", annot=False)
plt.title("Feature Correlation Heatmap")
plt.show()
```
Output:
This graph represents features that have a higher correlation marked red, lower correlation marked light blue and negative correlation marked blue


---

### [#9]


```
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

features = [f'V{i}' for i in range(1, 29)]
X = data[features]
y = data['Class']

# drop all NaN values
X = X.dropna()
y = y.dropna()

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

plt.figure(figsize=(10, 6))
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=y, alpha=0.5)
plt.title('PCA Projection of V1–V28')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.show()
```
Output:


---

### [#10]


```
# Visualize how this PCA matches up with our $ values
amount_values = data.loc[X.index, 'Amount']

# Create a scatter plot
plt.figure(figsize=(10, 6))
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=amount_values, alpha=0.5)
plt.title('PCA Projection of V1–V28')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.show()
```
Output:
Consider using t-SNE or UMAP...


---

### [#11]


```
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

# Sample to speed up t-SNE (adjust size as needed)
sampled_data = data.sample(n=5000, random_state=42)
features = [f'V{i}' for i in range(1, 29)]
X = sampled_data[features]
y = sampled_data['Class']

# Run t-SNE
tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
X_tsne = tsne.fit_transform(X)

# Visualize
tsne_df = pd.DataFrame({'TSNE1': X_tsne[:, 0], 'TSNE2': X_tsne[:, 1], 'Class': y.values})
plt.figure(figsize=(10, 6))
sns.scatterplot(data=tsne_df, x='TSNE1', y='TSNE2', hue='Class', alpha=0.6)
plt.title('t-SNE Projection of V1–V28')
plt.xlabel('t-SNE Component 1')
plt.ylabel('t-SNE Component 2')
plt.show()
```
Output:


---

### [#12]


```
import umap.umap_ as umap

# Use the same sampled data
reducer = umap.UMAP(n_components=2, random_state=42)
X_umap = reducer.fit_transform(X)

# Visualize
umap_df = pd.DataFrame({'UMAP1': X_umap[:, 0], 'UMAP2': X_umap[:, 1], 'Class': y.values})
plt.figure(figsize=(10, 6))
sns.scatterplot(data=umap_df, x='UMAP1', y='UMAP2', hue='Class', alpha=0.6)
plt.title('UMAP Projection of V1–V28')
plt.xlabel('UMAP Component 1')
plt.ylabel('UMAP Component 2')
plt.show()
```
Output:
I don't believe either of these will be as helpful.# Split data

---

### [#13]


```
# split the data between test and train, drop all NaN values
X = data.drop('Class', axis=1)
y = data['Class']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# X = data.drop('Class', axis=1)
# y = data['Class']
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(X.isna().sum())
print(y.isna().sum())
```
Output:
## Oversampling the imbalanced fraud data using SMOTE

---

### [#14]


```
smote = SMOTE(random_state=42)

# Drop all NaN values
X_train = X_train.dropna()
y_train = y_train.dropna()

X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

# Print class distribution
print("Class distribution before SMOTE:", Counter(y_train))
print("Class distribution after SMOTE:", Counter(y_train_smote))
```
Output:


---

### [#15]


```
# create a graph to visualize the new data spread
plt.figure(figsize=(10,5))
sns.countplot(x=y_train_smote)
plt.title("Fraud vs Non-Fraud Distribution ")
plt.show()
```
Output:


---

### [#16]


```
# Create a new graph to visualize the PCA components V1-V28
features = [f'V{i}' for i in range(1, 29)]
X = X_train_smote[features]
y = y_train_smote

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

plt.figure(figsize=(10, 6))
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=y, alpha=0.5)
plt.title('PCA Projection of V1–V28')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.show()
```
Output:
## Normalization

---

### [#17]


```
# data Standardization
scaler = StandardScaler()
X_train_smote_scaled = scaler.fit_transform(X_train_smote)
X_test_scaled = scaler.transform(X_test)
```


---

### [#18]


```
# Create a new graph after normalizing
features = [f'V{i}' for i in range(1, 29)]
X = X_train_smote_scaled
y = y_train_smote

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

plt.figure(figsize=(10, 6))
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=y, alpha=0.5)
plt.title('PCA Projection of V1–V28')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.show()
```
Output:


---

### [#19]


```
# Create new graphs that show individual data
features = [f'V{i}' for i in range(1, 29)]
X = X_train_smote_scaled
y = y_train_smote

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

# --- Graph for Class 0 ---
plt.figure(figsize=(10, 6))
sns.scatterplot(x=X_pca[y == 0, 0], y=X_pca[y == 0, 1], alpha=0.5) # Filter data for class 0
plt.title('PCA Projection of V1–V28 (Class 0)')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.show()

# --- Graph for Class 1 ---
plt.figure(figsize=(10, 6))
sns.scatterplot(x=X_pca[y == 1, 0], y=X_pca[y == 1, 1], alpha=0.5, color='orange') # Filter data for class 1
plt.title('PCA Projection of V1–V28 (Class 1)')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.show()
```
Output:
# Training Models

Logistic Regression

Random Forest

XGBoost

SVM (RBF kernel)

KNN## Logistic Regression


---

### [#20]


```
# Using a Logistic Regression model we will train the data points for classificaiton
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score, roc_curve, ConfusionMatrixDisplay, precision_recall_curve, auc

# train
model = LogisticRegression()
model.fit(X_train_smote_scaled, y_train_smote)

# predict
y_pred = model.predict(X_test_scaled)

# print results
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot()
plt.show()
print("Classification Report:\n", classification_report(y_test, y_pred))
```
Output:


---

### [#21]


```
# ROC and PR auc
print("ROC AUC:", roc_auc_score(y_test, y_pred))
precision, recall, thresholds = precision_recall_curve(y_test, y_pred)
pr_auc = auc(recall, precision)
print("PR AUC:", pr_auc)
```
Output:
The logistic regression model is pretty accurate, with an accuracy score of 0.99 and a recall accuracy of 0.86. There are only 22 improper classifications with this model, as opposed to 8315 proper classifications.## Random Forest

---

### [#22]


```
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# train
model = RandomForestClassifier()
model.fit(X_train_smote_scaled, y_train_smote)
```
Output:

```
RandomForestClassifier()
```


---

### [#23]


```
# predict
y_pred_rf = model.predict(X_test_scaled)

# print results
print("Accuracy:", accuracy_score(y_test, y_pred_rf))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_rf))
cm = confusion_matrix(y_test, y_pred_rf, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot()
plt.show()
print("Classification Report:\n", classification_report(y_test, y_pred_rf))
```
Output:


---

### [#24]


```
# ROC and PR auc
print("ROC AUC:", roc_auc_score(y_test, y_pred_rf))
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_rf)
pr_auc = auc(recall, precision)
print("PR AUC:", pr_auc)
```
Output:
The Random Forest model is even more accurate than the logistic regression model, with an accuracy score of 0.998## Support Vector Machine

---

### [#25]


```
# Use an SVM to predict fraud in addition to SMOTE
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# train
model = SVC(class_weight='balanced')
model.fit(X_train_smote_scaled, y_train_smote)
```
Output:

```
SVC(class_weight='balanced')
```


---

### [#26]


```
# predict
y_pred_svm = model.predict(X_test_scaled)

# results
print("Accuracy:", accuracy_score(y_test, y_pred_svm))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_svm))
cm = confusion_matrix(y_test, y_pred_svm, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot()
plt.show()
print("Classification Report:\n", classification_report(y_test, y_pred_svm))
```
Output:


---

### [#27]


```
# ROC and PR auc
print("ROC AUC:", roc_auc_score(y_test, y_pred_svm))
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_svm)
pr_auc = auc(recall, precision)
print("PR AUC:", pr_auc)
```
Output:
## KNN

---

### [#28]


```
# Train using a KNN on the standardized, SMOTE data
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

# Split data
X = data.drop('Class', axis=1)
y = data['Class']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Imputation using SimpleImputer for features (X)
imputer = SimpleImputer(strategy='mean')  # Or other strategies like 'median', 'most_frequent'
X_train_imputed = imputer.fit_transform(X_train)
X_test_imputed = imputer.transform(X_test)

# Since 'Class' is categorical, we might impute with the most frequent value
from sklearn.impute import SimpleImputer
imputer_y = SimpleImputer(strategy='most_frequent')
y_train = imputer_y.fit_transform(y_train.values.reshape(-1, 1))
y_test = imputer_y.transform(y_test.values.reshape(-1, 1))

# Now use X_train_imputed and X_test_imputed in the KNN model:
knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X_train_imputed, y_train.ravel()) # use ravel() to avoid warning

# Make Predictions
y_pred_knn = knn_model.predict(X_test_imputed)
```


---

### [#29]


```
# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred_knn))

# print results
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_knn))
cm = confusion_matrix(y_test, y_pred_knn, labels=knn_model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=knn_model.classes_)
disp.plot()
plt.show()
print("Classification Report:\n", classification_report(y_test, y_pred_knn))
```
Output:


---

### [#30]


```
# ROC and PR auc
print("ROC AUC:", roc_auc_score(y_test, y_pred_knn))
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_knn)
pr_auc = auc(recall, precision)
print("PR AUC:", pr_auc)
```
Output:
## XGBoost


---

### [#31]


```
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from xgboost import XGBClassifier
# train
xg_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
xg_model.fit(X_train_smote_scaled, y_train_smote)
```
Output:

```
XGBClassifier(base_score=None, booster=None, callbacks=None,
              colsample_bylevel=None, colsample_bynode=None,
              colsample_bytree=None, device=None, early_stopping_rounds=None,
              enable_categorical=False, eval_metric='logloss',
              feature_types=None, gamma=None, grow_policy=None,
              importance_type=None, interaction_constraints=None,
              learning_rate=None, max_bin=None, max_cat_threshold=None,
              max_cat_to_onehot=None, max_delta_step=None, max_depth=None,
              max_leaves=None, min_child_weight=None, missing=nan,
              monotone_constraints=None, multi_strategy=None, n_estimators=None,
              n_jobs=None, num_parallel_tree=None, random_state=None, ...)
```


---

### [#32]


```
# predict
y_pred_xg = xg_model.predict(X_test_scaled)

# print results
print("Accuracy:", accuracy_score(y_test, y_pred_xg))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_xg))
cm = confusion_matrix(y_test, y_pred_xg, labels=xg_model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=xg_model.classes_)
disp.plot()
plt.show()
print("Classification Report:\n", classification_report(y_test, y_pred_xg))
```
Output:


---

### [#33]


```
# ROC and PR auc
print("ROC AUC:", roc_auc_score(y_test, y_pred_xg))
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_xg)
pr_auc = auc(recall, precision)
print("PR AUC:", pr_auc)
```
Output:
