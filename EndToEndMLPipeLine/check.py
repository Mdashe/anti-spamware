import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri('http://127.0.0.1:5000')
client = MlflowClient()

print("Registered models:")
for rm in client.search_registered_models():
    print(" -", rm.name)

print("Versions for spam_ensemble:")
for v in client.search_model_versions("name='spam_ensemble'"):
    print(" -", v.version, v.current_stage)