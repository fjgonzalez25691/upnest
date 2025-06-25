import json
import os
import math
import pandas as pd
from scipy.stats import norm

data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Preload OMS tables (cache between invocations)
TABLES = {}

def load_table(sex):
    if sex == "male":
        key = "wfa-boys-zscore-expanded-tables.xlsx"
    else:
        key = "wfa-girls-zscore-expanded-tables.xlsx"
    if key not in TABLES:
        TABLES[key] = pd.read_excel(os.path.join(data_dir, 'weight', key))
    return TABLES[key]

def calculate_zscore(value, L, M, S):
    if L == 0:
        return math.log(value / M) / S
    else:
        return ((value / M) ** L - 1) / (L * S)

def zscore_to_percentile(z):
    return norm.cdf(z) * 100

def lambda_handler(event, context):
    """
    Lambda handler to compute weight percentile from OMS tables.
    Expects:
      - weight (kg)
      - date_birth, date_measurement (YYYY-MM-DD)
      - sex ('male' or 'female')
    """
    try:
        # Parse event body if it's a string (API Gateway)
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event
            
        # Basic validation   
        weight = float(body.get('weight'))
        date_birth = body.get('date_birth')
        date_measurement = body.get('date_measurement')
        sex = body.get('sex')
        if not all([weight, date_birth, date_measurement, sex]):
            raise ValueError("Missing one or more required fields")
        if sex not in ("male", "female"):
            raise ValueError("Sex must be 'male' or 'female'")

        # Load table and calculate age
        df = load_table(sex)
        age_days = (pd.to_datetime(date_measurement) - pd.to_datetime(date_birth)).days

        # Find exact or closest row
        row = df.loc[df['Day'] == age_days]
        if row.empty:
            # Find the closest age if the exact day is not present
            idx = (df['Day'] - age_days).abs().idxmin()
            row = df.loc[[idx]]

        L, M, S = float(row['L'].iloc[0]), float(row['M'].iloc[0]), float(row['S'].iloc[0])
    
        zscore = calculate_zscore(weight, L, M, S)
        percentile = round(zscore_to_percentile(zscore), 2)

        return {
            "input": event,
            "percentile": percentile,
            "zscore": zscore,
            "LMS": {"L": L, "M": M, "S": S},
            "success": True
        }
    except Exception as e:
        return {
            "input": event,
            "error": str(e),
            "success": False
        }

