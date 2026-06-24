"""Monitor incoming production data for drift and generate an Evidently report."""

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset

def run_drift_report(reference_path, production_path, output_path):
    """Run a data drift report and save it as HTML.

    Args:
        reference_path (str): Path to the reference dataset CSV file.
        production_path (str): Path to the current production dataset CSV file.
        output_path (str): Output path for the generated HTML report.

    The function reads the datasets, executes an Evidently report using the
    DataDriftPreset and ClassificationPreset, saves the report, and triggers
    retraining if dataset drift is detected.
    """

    ref  = pd.read_csv(reference_path)
    prod = pd.read_csv(production_path)
    report = Report(metrics=[
        DataDriftPreset(),       # feature distribution shift
        ClassificationPreset()   # precision/recall/F1 on labelled data
    ])
    report.run(reference_data=ref, current_data=prod)
    report.save_html(output_path)
    result = report.as_dict()
    if result['metrics'][0]['result']['dataset_drift']:
        print('ALERT: data drift detected — triggering retrain')
        import subprocess
        subprocess.run(['python', 'pipeline.py'])
