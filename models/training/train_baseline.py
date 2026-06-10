"""
Treina um modelo baseline TF-IDF + LogisticRegression para classificação de doenças.
Loga parâmetros, métricas e artefatos no MLflow (backend Postgres + artefatos MinIO).

Uso (dentro do container jupyter ou api):
    python models/training/train_baseline.py
"""
import os
import ast
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline

MINIO_OPTIONS = {
    "key": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
    "secret": os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin123"),
    "client_kwargs": {"endpoint_url": os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://minio:9000")},
}

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
EXPERIMENT_NAME = "triageai-baseline-oficial"
DATASET_PATH = "s3://gold/textos_rag.csv"
DATASET_VERSION = "1.0"


def load_data():
    df = pd.read_csv(DATASET_PATH, storage_options=MINIO_OPTIONS)
    df["sintomas"] = df["sintomas"].apply(ast.literal_eval)
    df["texto_sintomas"] = df["sintomas"].apply(lambda s: ", ".join(s))
    return df["texto_sintomas"].tolist(), df["diseases"].tolist()


def main():
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    params = {
        "model_type": "LogisticRegression",
        "vectorizer": "TfidfVectorizer",
        "tfidf_max_features": 10000,
        "tfidf_ngram_range": "(1, 2)",
        "lr_C": 1.0,
        "lr_max_iter": 1000,
        "dataset_version": DATASET_VERSION,
        "dataset_path": DATASET_PATH,
    }

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=params["tfidf_max_features"], ngram_range=(1, 2))),
        ("clf", LogisticRegression(C=params["lr_C"], max_iter=params["lr_max_iter"], random_state=42)),
    ])

    with mlflow.start_run(run_name="baseline-tfidf-lr"):
        mlflow.log_params(params)

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        mlflow.log_metric("accuracy", round(acc, 4))
        mlflow.log_metric("f1_score", round(f1, 4))

        mlflow.sklearn.log_model(pipeline, artifact_path="model", registered_model_name="triageai-baseline")

        print(f"[MLflow] Experimento: {EXPERIMENT_NAME}")
        print(f"[MLflow] accuracy={acc:.4f}  f1_score={f1:.4f}")
        print(f"[MLflow] Artefatos salvos em: s3://mlflow-artifacts/")


if __name__ == "__main__":
    main()
