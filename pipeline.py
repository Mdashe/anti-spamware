import yaml, pandas as pd, mlflow, mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from prefect import flow, task, get_run_logger
from src.preprocess import preprocess_text
from src.features  import build_vectorizer
from src.train     import train_models, log_run
from src.evaluate  import (compute_metrics, plot_confusion_matrices,
                            plot_roc_curves, plot_feature_importance)
from src.eda       import check_data_quality, plot_eda

with open('configs/config.yaml') as f: CFG = yaml.safe_load(f)

@task
def load_data():
    logger = get_run_logger()
    df = pd.read_csv(CFG['data']['raw_path'])
    logger.info(f'Loaded {len(df):,} rows')
    return df

