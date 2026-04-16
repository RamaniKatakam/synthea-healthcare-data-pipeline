import os
import sys
import logging
import argparse
from pathlib import Path
import yaml
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.getenv("PROJECT_ROOT")
default_config_path=os.path.join(PROJECT_ROOT, "config", "upload_config.yaml")
CONFIG_PATH = default_config_path if os.path.exists(default_config_path) else "./config/upload_config.yaml"
data_path = os.path.join(PROJECT_ROOT, "data")
DATA_DIR = data_path if os.path.exists(data_path) else "./data"
#keys_path = os.path.join(PROJECT_ROOT, "keys")
#KEYS_DIR = keys_path if os.path.exists(keys_path) else "./keys"

def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded config from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        sys.exit(1)


def upload_to_bigquery(file_path: str, table_name: str, project_id: str, dataset_id: str):
    """Upload a CSV file to BigQuery.
    
    Args:
        file_path: Path to the CSV file
        table_name: Name of the table in BigQuery
        project_id: GCP project ID
        dataset_id: BigQuery dataset ID
    """
    # Validate file exists
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        logger.info(f"Reading {file_path}...")
        df = pd.read_csv(file_path)
        
        table_id = f"{project_id}.{dataset_id}.{table_name}"
        logger.info(f"Uploading to {table_id}...")
        
        client = bigquery.Client(project=project_id)
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        job = client.load_table_from_dataframe(df, table_id,job_config=job_config)
        job.result()
        
        logger.info(f"✓ Successfully uploaded {file_path} to {table_id}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to upload {file_path}: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Upload Synthea CSV files to BigQuery'
    )
    parser.add_argument(
        '--config',
        default=CONFIG_PATH,
        help='Path to config file (default: config/upload_config.yaml)'
    )
    parser.add_argument(
        '--data-dir',
        default=DATA_DIR,
        help='Path to data directory (default: env var DATA_DIR or ./data)'
    )
    parser.add_argument(
        '--project-id',
        default=os.getenv('GCP_PROJECT_ID'),
        help='GCP Project ID (default: env var GCP_PROJECT_ID)'
    )
    parser.add_argument(
        '--dataset-id',
        default=os.getenv('BIGQUERY_DATASET', 'raw_synthea_data'),
        help='BigQuery Dataset ID (default: env var BIGQUERY_DATASET or raw_synthea_data)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Use command-line overrides or config values
    project_id = args.project_id or config.get('project_id')
    dataset_id = args.dataset_id or config.get('dataset_id')
    
    if not project_id:
        logger.error("Project ID not provided. Set GCP_PROJECT_ID env var or use --project-id")
        sys.exit(1)
    
    logger.info(f"Using project: {project_id}, dataset: {dataset_id}")
    
    # Upload files
    data_dir = Path(args.data_dir)
    success_count = 0
    
    for file_config in config.get('files', []):
        file_name = file_config['source']
        table_name = file_config['table']
        file_path = data_dir / file_name
        
        if upload_to_bigquery(str(file_path), table_name, project_id, dataset_id):
            success_count += 1
    
    logger.info(f"Upload complete: {success_count}/{len(config.get('files', []))} files uploaded")
    return 0 if success_count == len(config.get('files', [])) else 1


if __name__ == "__main__":
    sys.exit(main())