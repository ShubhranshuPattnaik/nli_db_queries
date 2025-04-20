import os

project_root_PATH: os.path = os.path.abspath("../")


def join_path(rel_path: str) -> str:
    pass


if os.path.basename(project_root_PATH) != "nli_db_queries":
    project_root_PATH = os.path.join(project_root_PATH, "nli_db_queries")

imdb_csv_folder_PATH: os.path = os.path.join(project_root_PATH, "imdb_ijs_csv")

cora_csv_folder_PATH: os.path = os.path.join(project_root_PATH, "CORA_csv")

financial_csv_folder_PATH: os.path = os.path.join(
    project_root_PATH, "financial_csv"
)

imdb_trunc_csv_folder_PATH: os.path = os.path.join(
    project_root_PATH, "imdb_ijs_truc_csv"
)

cora_trunc_csv_folder_PATH: os.path = os.path.join(
    project_root_PATH, "CORA_trunc_csv"
)

financial_trunc_csv_folder_PATH: os.path = os.path.join(
    project_root_PATH, "financial_trunc_csv"
)

db_data_loaders_PATH: os.path = os.path.join(
    project_root_PATH, "db_data_loaders"
)
