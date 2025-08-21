import pandas as pd
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_complaints_sample(file_path: str, sample_size: int = None) -> Optional[pd.DataFrame]:
    try:
        logger.info(f"Loading sample of {sample_size} rows from {file_path}")
        df = pd.read_csv(file_path, nrows=sample_size)
        logger.info(f"Successfully loaded {len(df)} records.")

        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None

def clean_complaint_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()

    for date_col in ['date_received', 'Date received', 'date']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            break


    narrative_col = 'consumer_complaint_narrative'
    if narrative_col not in df.columns:
        for col in df.columns:
            if 'narrative' in col.lower() or 'complaint' in col.lower():
                narrative_col = col
                break
            else:
                narrative_col = None
    if narrative_col:
        df['consumer_complaint_narrative'] = df[narrative_col].fillna('')
    else:
        df['consumer_complaint_narrative'] = ''

    df.columns = df.columns.str.lower().str.replace(' ', '_')

    expected_columns = [
            'company', 'product', 'sub_product', 'issue', 'sub_issue', 'state', 
            'zip_code', 'company_response', 'date_received', 
            'consumer_complaint_narrative', 'company_public_response', 'timely'
            ]
    available_columns = [col for col in expected_columns if col in df.columns]
    df = df[available_columns]

    logger.info(f"Data cleaning complete. Final shape: {df.shape}")
    return df

if __name__ == "__main__":
    file_path = "data/consumer_complaints.csv"

    raw_data = load_complaints_sample(file_path, sample_size=1000)

    if raw_data is not None:
        clean_data = clean_complaint_data(raw_data)

        print("✅ Data loaded and cleaned successfully!")
        print(f"Data shape: {clean_data.shape}")
        print(f"Columns: {clean_data.columns.tolist()}")
        print("\nFirst few rows:")
        print(clean_data.head())
    else:
        print("❌ Failed to load data")
