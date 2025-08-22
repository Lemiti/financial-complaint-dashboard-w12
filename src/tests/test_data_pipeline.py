import pandas as pd
import numpy as np
from data_pipeline import clean_complaint_data

def test_clean_complaint_data():

    sample_raw_data = pd.DataFrame({
        'Company': ['Bank of America', 'Wells Fargo', None],
        'Product': ['Credit card', 'Mortgage', 'Credit card'],
        'Sub-product': ['Rewards credit card', 'Conventional mortgage', np.nan],
        'Issue': ['Unexpected fees', 'Loan servicing issues', 'Fraud'],
        'Sub-issue': ['Balance transfer fee', 'Problems when you are unable to pay', np.nan],
        'Consumer complaint narrative': [
            'I was charged a hidden fee for balance transfer...',
            np.nan,
            'Unauthorized transactions on my account...'
        ],
        'State': ['CA', 'NY', 'TX'],
        'ZIP code': ['94105', '10001', '73301'],
        'Date received': ['2023-01-01', '2023-02-15', '2023-03-20']
    })

    cleaned_data = clean_complaint_data(sample_raw_data)

    assert 'company' in cleaned_data.columns
    assert 'sub_product' in cleaned_data.columns
    assert 'zip_code' in cleaned_data.columns

    assert 'consumer_complaint_narrative' in cleaned_data.columns
    assert cleaned_data['consumer_complaint_narrative'].isna().sum() == 0

    assert 'data_received' in cleaned_data.columns
    assert pd.api.type.is_datetime64_any_dtype(cleaned_data['date_received'])

    print("✅ All Kaggle data tests passed!")

if __name__ == "__main__":
    test_clean_complaint_data()
