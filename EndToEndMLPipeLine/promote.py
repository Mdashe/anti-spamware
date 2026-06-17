import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri('http://127.0.0.1:5000')
client = MlflowClient()

for v in client.get_latest_versions('spam_ensemble', stages=['Staging']):
    print(f'  v{v.version}  run_id={v.run_id}')

client.transition_model_version_stage(
    name='spam_ensemble', version='1', stage='Production')