

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
import joblib
import json

# ============================================================
# 1. LOAD DATASET
# ============================================================
print("=" * 60)
print("1. Loading dataset...")
df = pd.read_csv("data_clean.csv")
print(f"   Total data: {len(df)} baris")
print(f"   Distribusi label:\n{df['label'].value_counts()}")

# ============================================================
# 2. PILIH FITUR (kolom numerik saja, exclude url/dom/tld/label)
# ============================================================
FEATURE_COLS = [
    "url_len", "dom_len", "is_ip", "tld_len", "subdom_cnt",
    "letter_cnt", "digit_cnt", "special_cnt", "eq_cnt", "qm_cnt",
    "amp_cnt", "dot_cnt", "dash_cnt", "under_cnt", "letter_ratio",
    "digit_ratio", "spec_ratio", "is_https", "slash_cnt", "entropy",
    "path_len", "query_len"
]

X = df[FEATURE_COLS].copy()
y = df["label"].copy()

print(f"\n2. Jumlah fitur dipakai: {len(FEATURE_COLS)}")
print(f"   {FEATURE_COLS}")

# ============================================================
# 3. SPLIT DATA (80% train, 20% test) - stratify biar proporsi label sama
# ============================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n3. Split data: train={len(X_train)}, test={len(X_test)}")

# ============================================================
# 4. SCALING (StandardScaler) - disimpan juga buat dipakai di app
# ============================================================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================
# 5. TRAINING RANDOM FOREST
# ============================================================
print("\n4. Training Random Forest...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight="balanced",   # handle imbalance (87% vs 13%)
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_scaled, y_train)
print("   Training selesai.")

# ============================================================
# 6. EVALUASI
# ============================================================
y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("\n" + "=" * 60)
print("HASIL EVALUASI MODEL")
print("=" * 60)
print(f"Accuracy   : {acc:.4f} ({acc*100:.2f}%)")
print(f"Precision  : {prec:.4f} ({prec*100:.2f}%)")
print(f"Recall     : {rec:.4f} ({rec*100:.2f}%)")
print(f"F1-Score   : {f1:.4f} ({f1*100:.2f}%)")
print("\nConfusion Matrix:")
print(cm)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Legitimate", "Phishing"]))

# ============================================================
# 7. FEATURE IMPORTANCE
# ============================================================
importance = pd.DataFrame({
    "feature": FEATURE_COLS,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("\nTop 10 Feature Importance:")
print(importance.head(10).to_string(index=False))

# ============================================================
# 8. SIMPAN MODEL + SCALER + METADATA
# ============================================================
artifact = {
    "model": model,
    "scaler": scaler,
    "feature_cols": FEATURE_COLS,
    "metrics": {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "confusion_matrix": cm.tolist()
    }
}

joblib.dump(artifact, "model_rf.pkl")
print("\n" + "=" * 60)
print("Model tersimpan di: model_rf.pkl")
print("=" * 60)

# Simpan juga metrics ke json (buat ditampilkan di app nanti)
with open("metrics.json", "w") as f:
    json.dump({
        "accuracy": acc, "precision": prec, "recall": rec,
        "f1_score": f1, 
        "confusion_matrix": cm.tolist(),
        "feature_importance": importance.to_dict(orient="records")
    }, f, indent=2)
print("Metrics tersimpan di: metrics.json")
