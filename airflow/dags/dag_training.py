# """
# DAG de treinamento de modelos — Sprint 4
# Responsável: MLOps/Infra (estrutura) + Time de ML (modelo)
# Integração com MLflow para tracking de experimentos
# """

# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime


# def run_training():
#     """
#     Esqueleto de treino (o time de ML implementa o modelo aqui)*
#     integração com MLflow configurada
    
#     """
#     import mlflow

#     mlflow.set_tracking_uri("http://mlflow:5000")
#     mlflow.set_experiment("triageai-training")

#     with mlflow.start_run():
        
#         # TIME DE ML: substitua o bloco abaixo pelo treino real

#         mlflow.log_param("model", "placeholder")
#         mlflow.log_param("dataset", "bronze")
#         mlflow.log_metric("accuracy", 0.0)
#         mlflow.log_metric("f1_score", 0.0)

#         # -------------------------------------------------------

#         print("Experimento registrado no MLflow")


# def validate_model():
#     """Validação pós treino."""
#     print("Validando modelo...")
#     print("Validação concluída")


# with DAG(
#     dag_id="pipeline_training",
#     description="Pipeline de treinamento com tracking no MLflow",
#     start_date=datetime(2025, 1, 1),
#     schedule_interval="@weekly",
#     catchup=False,
#     tags=["training", "mlflow", "sprint4"],
# ) as dag:

#     train    = PythonOperator(task_id="run_training",    python_callable=run_training)
#     validate = PythonOperator(task_id="validate_model",  python_callable=validate_model)

#     train >> validate