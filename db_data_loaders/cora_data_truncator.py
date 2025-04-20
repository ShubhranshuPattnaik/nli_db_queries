import pandas as pd
from pathlib import Path
from path_utils import Path_Handler as ph
import os

# === Load original CSVs ===
paper_df = pd.read_csv(os.path.join(ph.cora_csv_folder_PATH, "paper.csv"))
content_df = pd.read_csv(os.path.join(ph.cora_csv_folder_PATH, "content.csv"))
cites_df = pd.read_csv(os.path.join(ph.cora_csv_folder_PATH, "cites.csv"))

# === Parameters ===
sample_size = 1500
random_state = 42
output_dir = os.path.join(ph.project_root_PATH, "CORA_trunc_csv")
os.makedirs(output_dir, exist_ok=True)

# === Step 1: Sample papers ===
sampled_ids = set(
    paper_df["paper_id"].sample(n=sample_size, random_state=random_state)
)

# === Step 2: Filter paper.csv ===
reduced_paper_df = paper_df[paper_df["paper_id"].isin(sampled_ids)]

# === Step 3: Filter content.csv ===
reduced_content_df = content_df[content_df["paper_id"].isin(sampled_ids)]

# === Step 4: Filter cites.csv ===
reduced_cites_df = cites_df[
    cites_df["citing_paper_id"].isin(sampled_ids)
    & cites_df["cited_paper_id"].isin(sampled_ids)
]

# === Step 5: Save outputs ===
reduced_paper_df.to_csv(os.path.join(output_dir, "paper.csv"), index=False)
reduced_content_df.to_csv(os.path.join(output_dir, "content.csv"), index=False)
reduced_cites_df.to_csv(os.path.join(output_dir, "cites.csv"), index=False)

# === Step 6: Print summary ===
print("✅ Reduction completed.")
print(f"📄 paper.csv: {len(reduced_paper_df)} rows")
print(f"📄 content.csv: {len(reduced_content_df)} rows")
print(f"📄 cites.csv: {len(reduced_cites_df)} rows")
