import os
import pandas as pd
from utils import Path_Handler as ph


db_names: list[str] = [
    "imdb_ijs",
    "financial",
    "CORA",
]
csv_folder_paths: list = [
    ph.imdb_csv_folder_PATH,
    ph.financial_csv_folder_PATH,
    ph.cora_csv_folder_PATH,
]


def infer_sql_type(series):
    if pd.api.types.is_integer_dtype(series):
        return "INT"
    elif pd.api.types.is_float_dtype(series):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "DATETIME"
    else:
        max_len = series.astype(str).str.len().max()
        return f"VARCHAR({int(max_len) + 50 if not pd.isna(max_len) else 255})"


for db_name, input_folder in zip(db_names, csv_folder_paths):
    # Input folder with CSVs
    # input_folder = f"{db_name}_csv"
    # Output SQL file
    output_sql_file = f"{ph.db_data_loaders_PATH}/{db_name}_data.sql"

    if os.path.exists(output_sql_file):
        os.remove(output_sql_file)

    with open(output_sql_file, "w", encoding="utf-8") as sql_file:
        sql_file.write(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;\n\n")
        sql_file.write(f"USE `{db_name}`;\n\n")
        for filename in os.listdir(input_folder):
            if filename.endswith(".csv"):
                table_name = os.path.splitext(filename)[0]
                csv_path = os.path.join(input_folder, filename)
                print(f"Reading file: {csv_path}", end="\n*******\n")
                df = pd.read_csv(csv_path, low_memory=False)

                # Generate CREATE TABLE
                sql_file.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
                sql_file.write(f"CREATE TABLE `{table_name}` (\n")
                columns = []
                for col in df.columns:
                    col_type = infer_sql_type(df[col])
                    col_clean = col.replace(
                        "`", ""
                    )  # remove accidental backticks
                    columns.append(f"  `{col_clean}` {col_type}")
                sql_file.write(",\n".join(columns))
                sql_file.write("\n);\n\n")

                # Bulk insert from csv
                sql_file.write(
                    f"LOAD DATA LOCAL INFILE '{os.path.abspath(csv_path)}'\nINTO TABLE `{table_name}`\nFIELDS TERMINATED BY ','\nENCLOSED BY '\"'\nLINES TERMINATED BY '\\n'\nIGNORE 1 LINES;\n\n"
                )
                # Generate INSERT INTO
                # for _, row in df.iterrows():
                #     values = []
                #     for val in row:
                #         if pd.isna(val):
                #             values.append("NULL")
                #         elif isinstance(val, (int, float)):
                #             values.append(str(val))
                #         else:
                #             val_escaped = str(val).replace("'", "''")
                #             values.append(f"'{val_escaped}'")
                #     sql_file.write(
                #         f"INSERT INTO `{table_name}` VALUES ({', '.join(values)});\n"
                #     )
                # sql_file.write("\n")

    print(f"SQL dump generated: {output_sql_file}")
