import os
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from dateutil import parser
import re
import path_utils.Path_Handler as ph


# Path where CSV files are stored
base_path = [
    ph.imdb_trunc_csv_folder_PATH,
    ph.financial_trunc_csv_folder_PATH,
    ph.cora_trunc_csv_folder_PATH,
]

# Define accepted date formats
date_formats = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y",  # Just year
    "%B %d, %Y",  # e.g. January 15, 2021
]


# Try to parse a string into a date
def try_parse_date(val):
    for fmt in date_formats:
        try:
            return datetime.strptime(val, fmt)
        except (ValueError, TypeError):
            continue
    try:
        return parser.parse(val)
    except Exception:
        return None


# Convert individual cell values to appropriate types
def convert_cell(val):
    import numpy as np

    if pd.isna(val):
        return None

    # Convert numpy types to native Python types
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    if isinstance(val, (np.floating, np.float64, np.float32)):
        return float(val)
    if isinstance(val, (np.bool_)):
        return bool(val)

    # Keep datetime and plain Python types as-is
    if isinstance(val, (int, float, bool, str, datetime)):
        return val

    if isinstance(val, str):
        val = val.strip()

        # Check int
        if re.fullmatch(r"[-+]?\d+", val):
            return int(val)

        # Check float
        if re.fullmatch(r"[-+]?\d*\.\d+", val):
            return float(val)

        # Try date
        parsed = try_parse_date(val)
        if parsed:
            return parsed

    return val  # fallback


# Convert a DataFrame into list of typed dictionaries
def df_to_typed_dicts(df):
    records = []
    for _, row in df.iterrows():
        typed_row = {col: convert_cell(row[col]) for col in df.columns}
        records.append(typed_row)
    return records


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Loop through and import each CSV
for folder_path in base_path:
    for file_path in os.listdir(folder_path):
        db_name = str(os.path.basename(folder_path))[:-4]
        collection_name = os.path.splitext(file_path)[0]
        db = client[db_name]
        full_path = os.path.join(folder_path, file_path)

        if collection_name in db.list_collection_names():
            print(f"⚠️ Collection `{collection_name}` exists. Dropping it.")
            db.drop_collection(collection_name)

        print(f"⏳ Loading {file_path} into collection `{collection_name}`")

        df = pd.read_csv(full_path)
        records = df_to_typed_dicts(df)

        # Insert into MongoDB
        if records:
            db[collection_name].insert_many(records)
            print(
                f"✅ Inserted {len(records)} documents into `{collection_name}`"
            )

    print("🎉 All files imported with correct types.")
