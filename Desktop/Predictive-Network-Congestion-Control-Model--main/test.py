import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, precision_recall_curve
from imblearn.over_sampling import SMOTE


data = pd.read_csv('network_congestion_data.csv')


data['congestion'] = data['IPv4 bytes'].apply(lambda x: 1 if x > 1e10 else 0)

features = data.drop('congestion', axis=1)
noise = np.random.normal(0, 1, features.shape)
features_noisy = features + noise

data_noisy = features_noisy.copy()
data_noisy['congestion'] = data['congestion']

X = data_noisy.drop('congestion', axis=1)
y = data_noisy['congestion']

smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)

model = LogisticRegression(random_state=42)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_res, y_res, cv=cv)

model.fit(X_train, y_train)
y_prob = model.predict_proba(X_test)[:, 1]

thresholds = np.linspace(0, 1, 200)
best_thresh = 0.5
min_diff = float('inf')

for t in thresholds:
    preds = (y_prob >= t).astype(int)
    diff = abs(np.sum(preds) - len(preds) / 2)
    if diff < min_diff:
        min_diff = diff
        best_thresh = t

y_pred_balanced = (y_prob >= best_thresh).astype(int)
cm = confusion_matrix(y_test, y_pred_balanced)

print("\nCross-validation scores:", cv_scores)
print("\nAverage CV score:", cv_scores.mean())
print("\nClassification Report at threshold {:.3f}:\n".format(best_thresh), classification_report(y_test, y_pred_balanced))

fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)
precision, recall, pr_thresholds = precision_recall_curve(y_test, y_prob)


fig, axs = plt.subplots(1, 3, figsize=(24, 6))


axs[0].plot(fpr, tpr, color='blue', lw=2, label=f'ROC AUC = {roc_auc:.2f}')
axs[0].plot([0, 1], [0, 1], linestyle='--', color='gray')
axs[0].set_title('ROC Curve')
axs[0].set_xlabel('False Positive Rate')
axs[0].set_ylabel('True Positive Rate')
axs[0].legend()

# Confusion Matrix
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axs[1],
            xticklabels=['Not Congested', 'Congested'],
            yticklabels=['Not Congested', 'Congested'])
axs[1].set_title(f'Confusion Matrix\n(Threshold = {best_thresh:.3f})')
axs[1].set_xlabel('Predicted')
axs[1].set_ylabel('Actual')

# Precision-Recall Curve
axs[2].plot(recall, precision, color='green', lw=2)
axs[2].set_title('Precision-Recall Curve')
axs[2].set_xlabel('Recall')
axs[2].set_ylabel('Precision')

# Highlight the balanced threshold on PR curve (optional)
# Find the closest point to best_thresh
if len(pr_thresholds) > 0:
    closest_idx = np.argmin(np.abs(pr_thresholds - best_thresh))
    axs[2].plot(recall[closest_idx], precision[closest_idx], 'ro', label=f'Threshold = {best_thresh:.3f}')
    axs[2].legend()

plt.tight_layout()
plt.show()