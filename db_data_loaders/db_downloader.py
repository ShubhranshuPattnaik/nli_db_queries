import mysql.connector
import pandas as pd
import os
from utils import Path_Handler as ph

# Connection settings
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

for db_name, output_folder in zip(db_names, csv_folder_paths):
    config = {
        "host": "relational.fel.cvut.cz",
        "port": 3306,
        "user": "guest",
        "password": "ctu-relational",
        "database": db_name,
    }

    # Output folder
    # output_folder = f"{db_name}_csv"
    os.makedirs(output_folder, exist_ok=True)

    try:
        # Connect to the database
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"Found {len(tables)} tables. Exporting to CSV...")

        # Export each table to CSV
        for table in tables:
            query = f"SELECT * FROM `{table}`;"
            df = pd.read_sql(query, conn)
            csv_path = os.path.join(output_folder, f"{table}.csv")
            df.to_csv(csv_path, index=False)
            print(f"Saved {table} to {csv_path}")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if "conn" in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Connection closed.")
