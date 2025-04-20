import pandas as pd
import os
from path_utils import Path_Handler as ph

# === INPUT/OUTPUT FOLDERS ===
base_path = ph.financial_csv_folder_PATH
output_path = os.path.join(ph.project_root_PATH, "./financial_trunc_csv")
os.makedirs(output_path, exist_ok=True)

# === FILES TO LOAD ===
files = {
    "account": "account.csv",
    "card": "card.csv",
    "client": "client.csv",
    "disp": "disp.csv",
    "district": "district.csv",
    "loan": "loan.csv",
    "order": "order.csv",
    "trans": "trans.csv",
}

# === LOAD DATAFRAMES ===
dfs = {
    name: pd.read_csv(os.path.join(base_path, fname))
    for name, fname in files.items()
}

# === STEP 1: Sample Accounts ===
sampled_accounts = dfs["account"].sample(n=1500, random_state=42)
sampled_account_ids = set(sampled_accounts["account_id"])

# === STEP 2: Filter disp ===
reduced_disp = dfs["disp"][dfs["disp"]["account_id"].isin(sampled_account_ids)]
sampled_client_ids = set(reduced_disp["client_id"])
sampled_disp_ids = set(reduced_disp["disp_id"])

# === STEP 3: Filter client ===
reduced_client = dfs["client"][
    dfs["client"]["client_id"].isin(sampled_client_ids)
]
sampled_district_ids = set(reduced_client["district_id"])

# === STEP 4: Filter district ===
reduced_district = dfs["district"][
    dfs["district"]["district_id"].isin(sampled_district_ids)
]

# === STEP 5: Filter card ===
reduced_card = dfs["card"][dfs["card"]["disp_id"].isin(sampled_disp_ids)]

# === STEP 6: Filter loan ===
reduced_loan = dfs["loan"][dfs["loan"]["account_id"].isin(sampled_account_ids)]

# === STEP 7: Filter order ===
reduced_order = dfs["order"][
    dfs["order"]["account_id"].isin(sampled_account_ids)
]
reduced_order = reduced_order.groupby("account_id").head(2)

# === STEP 8: Filter trans ===
reduced_trans = dfs["trans"][
    dfs["trans"]["account_id"].isin(sampled_account_ids)
]
reduced_trans = reduced_trans.groupby("account_id").head(5)

# === SAVE ALL REDUCED FILES ===
reduced_datasets = {
    "account": sampled_accounts,
    "disp": reduced_disp,
    "client": reduced_client,
    "district": reduced_district,
    "card": reduced_card,
    "loan": reduced_loan,
    "order": reduced_order,
    "trans": reduced_trans,
}

for name, df in reduced_datasets.items():
    output_file = os.path.join(output_path, f"{name}.csv")
    df.to_csv(output_file, index=False)
    print(f"✅ Saved: {output_file} ({len(df)} rows)")
