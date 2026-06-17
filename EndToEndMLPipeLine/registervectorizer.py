import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri('http://127.0.0.1:5000')

result = mlflow.register_model(
    'runs:/f371e1fa653242b49e99cc46fa8928f4/tfidf_vectorizer',
    'tfidf_vectorizer')

client = MlflowClient()
client.transition_model_version_stage(
    name='tfidf_vectorizer', version=result.version, stage='Production')

print(f'tfidf_vectorizer v{result.version} promoted to Production')