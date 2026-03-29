import time
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, f1_score, recall_score, precision_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import warnings

warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "creditcard_scaled.csv"

def load_data(filepath: Path):
    print(f"Loading preprocessed dataset from: {filepath}")
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found at: {filepath}. Run 01_eda_and_preprocessing.py first.")
    
    df = pd.read_csv(filepath)
    X = df.drop('Class', axis=1)
    y = df['Class']
    return X, y

def run_model_benchmark(X, y):
    print("\nStarting Model Benchmarking Phase...")
    print("-" * 50)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    neg_class_count = (y_train == 0).sum()
    pos_class_count = (y_train == 1).sum()
    scale_pos_weight_val = neg_class_count / pos_class_count
    
    print(f"Training Set Shape: {X_train.shape}")
    print(f"Class Imbalance Ratio (Neg/Pos): {scale_pos_weight_val:.2f}")
    print("-" * 50)

    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            class_weight='balanced',
            n_jobs=-1,
            random_state=42
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=100,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
            verbose=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100,
            scale_pos_weight=scale_pos_weight_val,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss'
        )
    }

    results = []

    for model_name, model in models.items():
        print(f"Training {model_name}...")
        
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        inf_start_time = time.time()
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        inference_time = (time.time() - inf_start_time) / len(X_test) * 1000 
        
        pr_auc = average_precision_score(y_test, y_prob)
        recall = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        results.append({
            "Model": model_name,
            "PR-AUC": round(pr_auc, 4),
            "Recall": round(recall, 4),
            "Precision": round(precision, 4),
            "F1-Score": round(f1, 4),
            "Train Time (s)": round(train_time, 2),
            "Inf. Time/Row (ms)": round(inference_time, 4)
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="PR-AUC", ascending=False).reset_index(drop=True)
    
    print("\n" + "="*80)
    print(" "*25 + "BENCHMARK RESULTS")
    print("="*80)
    print(results_df.to_string(index=False))
    print("="*80)
    
    return results_df

if __name__ == "__main__":
    X, y = load_data(PROCESSED_DATA_PATH)
    benchmark_results = run_model_benchmark(X, y)
    
    best_model = benchmark_results.iloc[0]['Model']
    print(f"\nRecommended Model for Production: {best_model}")