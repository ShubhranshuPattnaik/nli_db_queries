class SchemaLoader:
    def __init__(self):
        # Full table schemas
        self.schemas = {
            "cora": {
                "content": """
                    Table: content
                    - paper_id: INT
                    - word_cited_id: VARCHAR(58)
                    """,
                "cites": """
                    Table: cites
                    - cited_paper_id: INT
                    - citing_paper_id: INT
                    """,
                "paper": """
                    Table: paper
                    - paper_id: INT
                    - class_label: VARCHAR(72)
                    """,
            },
            "financial": {
                "client": """
                    Table: client
                    - client_id: INT
                    - gender: VARCHAR(51)
                    - birth_date: DATE
                    - district_id: INT
                    """,
                "trans": """
                    Table: trans
                    - trans_id: INT
                    - account_id: INT
                    - date: DATE
                    - type: VARCHAR(56)
                    - operation: VARCHAR(64)
                    - amount: INT
                    - balance: INT
                    - k_symbol: VARCHAR(61)
                    - bank: VARCHAR(53)
                    - account: FLOAT
                    """,
                "district": """
                    Table: district
                    - district_id: INT
                    - A2 to A16: mixed types (mostly INT/FLOAT)
                    """,
                "account": """
                    Table: account
                    - account_id: INT
                    - district_id: INT
                    - frequency: VARCHAR(68)
                    - date: DATE
                    """,
                "card": """
                    Table: card
                    - card_id: INT
                    - disp_id: INT
                    - type: VARCHAR(57)
                    - issued: DATE
                    """,
                "loan": """
                    Table: loan
                    - loan_id: INT
                    - account_id: INT
                    - date: DATE
                    - amount: INT
                    - duration: INT
                    - payments: FLOAT
                    - status: VARCHAR(51)
                    """,
                "order": """
                    Table: order
                    - order_id: INT
                    - account_id: INT
                    - bank_to: VARCHAR(52)
                    - account_to: INT
                    - amount: FLOAT
                    - k_symbol: VARCHAR(58)
                    """,
                "disp": """
                    Table: disp
                    - disp_id: INT
                    - client_id: INT
                    - account_id: INT
                    - type: VARCHAR(59)
                    """,
            },
            "imdb_ijs": {
                "movies_genres": """
                    Table: movies_genres
                    - movie_id: INT
                    - genre: VARCHAR(61)
                    """,
                "directors_genres": """
                    Table: directors_genres
                    - director_id: INT
                    - genre: VARCHAR(61)
                    - prob: FLOAT
                    """,
                "movies_directors": """
                    Table: movies_directors
                    - director_id: INT
                    - movie_id: INT
                    """,
                "actors": """
                    Table: actors
                    - id: INT
                    - first_name: VARCHAR(80)
                    - last_name: VARCHAR(80)
                    - gender: VARCHAR(51)
                    """,
                "roles": """
                    Table: roles
                    - actor_id: INT
                    - movie_id: INT
                    - role: VARCHAR(80)
                    """,
                "directors": """
                    Table: directors
                    - id: INT
                    - first_name: VARCHAR(80)
                    - last_name: VARCHAR(76)
                    """,
                "movies": """
                    Table: movies
                    - id: INT
                    - name: VARCHAR(150)
                    - year: INT
                    - rank: FLOAT
                    """,
            },
        }

        # Table relationship mapping (for JOIN-based prompts)
        self.related_table_map = {
            "financial": {
                "client": ["client", "disp", "account", "trans"],
                "trans": ["client", "disp", "account", "trans"],
                "loan": ["loan", "account", "disp", "client"],
                "order": ["order", "account", "disp", "client"],
            },
            "imdb_ijs": {
                "movies": [
                    "movies",
                    "movies_directors",
                    "directors",
                    "movies_genres",
                ],
                "actors": ["actors", "roles", "movies"],
                "directors": ["directors", "movies_directors", "movies"],
            },
            "cora": {"paper": ["paper", "cites"], "cites": ["paper", "cites"]},
        }

    def get_schema(self, db_name, table_name=None):
        db = db_name.lower()
        if db not in self.schemas:
            return "Schema not available."

        # If no table mentioned → inject full DB schema
        if not table_name:
            return "\n".join(self.schemas[db].values())

        table = table_name.lower()

        # If related tables defined, inject them all
        related_tables = self.related_table_map.get(db, {}).get(table, [table])
        return "\n".join(
            self.schemas[db].get(t, "")
            for t in related_tables
            if t in self.schemas[db]
        )
