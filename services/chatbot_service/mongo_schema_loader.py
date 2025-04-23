from typing import Optional


class MongoSchemaLoader:
    def __init__(self):
        self.schema = {
            "imdb_ijs": {
                "movies_genres": {
                    "movie_id": {"type": "int", "ref": ("movies", "id")},
                    "genre": {"type": "string"},
                },
                "directors_genres": {
                    "director_id": {"type": "int", "ref": ("directors", "id")},
                    "genre": {"type": "string"},
                    "prob": {"type": "float"},
                },
                "movies_directors": {
                    "director_id": {"type": "int", "ref": ("directors", "id")},
                    "movie_id": {"type": "int", "ref": ("movies", "id")},
                },
                "actors": {
                    "id": {"type": "int"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "gender": {"type": "string"},
                },
                "roles": {
                    "actor_id": {"type": "int", "ref": ("actors", "id")},
                    "movie_id": {"type": "int", "ref": ("movies", "id")},
                    "role": {"type": "string"},
                },
                "directors": {
                    "id": {"type": "int"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                },
                "movies": {
                    "id": {"type": "int"},
                    "name": {"type": "string"},
                    "year": {"type": "int"},
                    "rank": {"type": "float"},
                },
            },
            "financial": {
                "client": {
                    "client_id": {"type": "int"},
                    "gender": {"type": "string"},
                    "birth_date": {"type": "ISODate"},
                    "district_id": {
                        "type": "int",
                        "ref": ("district", "district_id"),
                    },
                },
                "trans": {
                    "trans_id": {"type": "int"},
                    "account_id": {
                        "type": "int",
                        "ref": ("account", "account_id"),
                    },
                    "date": {"type": "ISODate"},
                    "type": {"type": "string"},
                    "operation": {"type": "string"},
                    "amount": {"type": "int"},
                    "balance": {"type": "int"},
                    "k_symbol": {"type": "string"},
                    "bank": {"type": "string"},
                    "account": {"type": "float"},
                },
                "district": {
                    "district_id": {"type": "int"},
                    "A2": {"type": "string"},
                    "A3": {"type": "string"},
                    "A4": {"type": "int"},
                    "A5": {"type": "int"},
                    "A6": {"type": "int"},
                    "A7": {"type": "int"},
                    "A8": {"type": "int"},
                    "A9": {"type": "int"},
                    "A10": {"type": "float"},
                    "A11": {"type": "int"},
                    "A12": {"type": "float"},
                    "A13": {"type": "float"},
                    "A14": {"type": "int"},
                    "A15": {"type": "float"},
                    "A16": {"type": "int"},
                },
                "account": {
                    "account_id": {"type": "int"},
                    "district_id": {
                        "type": "int",
                        "ref": ("district", "district_id"),
                    },
                    "frequency": {"type": "string"},
                    "date": {"type": "ISODate"},
                },
                "card": {
                    "card_id": {"type": "int"},
                    "disp_id": {"type": "int", "ref": ("disp", "disp_id")},
                    "type": {"type": "string"},
                    "issued": {"type": "ISODate"},
                },
                "loan": {
                    "loan_id": {"type": "int"},
                    "account_id": {
                        "type": "int",
                        "ref": ("account", "account_id"),
                    },
                    "date": {"type": "ISODate"},
                    "amount": {"type": "int"},
                    "duration": {"type": "int"},
                    "payments": {"type": "float"},
                    "status": {"type": "string"},
                },
                "order": {
                    "order_id": {"type": "int"},
                    "account_id": {
                        "type": "int",
                        "ref": ("account", "account_id"),
                    },
                    "account_to": {
                        "type": "int",
                        "ref": ("account", "account_id"),
                    },
                    "bank_to": {"type": "string"},
                    "amount": {"type": "float"},
                    "k_symbol": {"type": "string"},
                },
                "disp": {
                    "disp_id": {"type": "int"},
                    "client_id": {
                        "type": "int",
                        "ref": ("client", "client_id"),
                    },
                    "account_id": {
                        "type": "int",
                        "ref": ("account", "account_id"),
                    },
                    "type": {"type": "string"},
                },
            },
            "cora": {
                "content": {
                    "paper_id": {"type": "int", "ref": ("paper", "paper_id")},
                    "word_cited_id": {"type": "string"},
                },
                "cites": {
                    "cited_paper_id": {
                        "type": "int",
                        "ref": ("paper", "paper_id"),
                    },
                    "citing_paper_id": {
                        "type": "int",
                        "ref": ("paper", "paper_id"),
                    },
                },
                "paper": {
                    "paper_id": {"type": "int"},
                    "class_label": {"type": "string"},
                },
            },
        }

        self.relations = {
            "imdb_ijs": [
                {
                    "from": "movies_genres",
                    "local_field": "movie_id",
                    "foreign_collection": "movies",
                    "foreign_field": "id",
                },
                {
                    "from": "directors_genres",
                    "local_field": "director_id",
                    "foreign_collection": "directors",
                    "foreign_field": "id",
                },
                {
                    "from": "movies_directors",
                    "local_field": "director_id",
                    "foreign_collection": "directors",
                    "foreign_field": "id",
                },
                {
                    "from": "movies_directors",
                    "local_field": "movie_id",
                    "foreign_collection": "movies",
                    "foreign_field": "id",
                },
                {
                    "from": "roles",
                    "local_field": "actor_id",
                    "foreign_collection": "actors",
                    "foreign_field": "id",
                },
                {
                    "from": "roles",
                    "local_field": "movie_id",
                    "foreign_collection": "movies",
                    "foreign_field": "id",
                },
            ],
            "financial": [
                {
                    "from": "client",
                    "local_field": "district_id",
                    "foreign_collection": "district",
                    "foreign_field": "district_id",
                },
                {
                    "from": "trans",
                    "local_field": "account_id",
                    "foreign_collection": "account",
                    "foreign_field": "account_id",
                },
                {
                    "from": "account",
                    "local_field": "district_id",
                    "foreign_collection": "district",
                    "foreign_field": "district_id",
                },
                {
                    "from": "card",
                    "local_field": "disp_id",
                    "foreign_collection": "disp",
                    "foreign_field": "disp_id",
                },
                {
                    "from": "loan",
                    "local_field": "account_id",
                    "foreign_collection": "account",
                    "foreign_field": "account_id",
                },
                {
                    "from": "order",
                    "local_field": "account_id",
                    "foreign_collection": "account",
                    "foreign_field": "account_id",
                },
                {
                    "from": "order",
                    "local_field": "account_to",
                    "foreign_collection": "account",
                    "foreign_field": "account_id",
                },
                {
                    "from": "disp",
                    "local_field": "client_id",
                    "foreign_collection": "client",
                    "foreign_field": "client_id",
                },
                {
                    "from": "disp",
                    "local_field": "account_id",
                    "foreign_collection": "account",
                    "foreign_field": "account_id",
                },
            ],
            "cora": [
                {
                    "from": "content",
                    "local_field": "paper_id",
                    "foreign_collection": "paper",
                    "foreign_field": "paper_id",
                },
                {
                    "from": "cites",
                    "local_field": "cited_paper_id",
                    "foreign_collection": "paper",
                    "foreign_field": "paper_id",
                },
                {
                    "from": "cites",
                    "local_field": "citing_paper_id",
                    "foreign_collection": "paper",
                    "foreign_field": "paper_id",
                },
            ],
        }

    def get_schema(self, db_name: str, collection_name: Optional[str] = None):
        if db_name not in self.schema:
            raise ValueError(f"Database '{db_name}' not found.")

        db = self.schema[db_name]

        if collection_name is None:
            related_collections = db
        else:
            if collection_name not in db:
                raise ValueError(
                    f"Collection '{collection_name}' not found in database '{db_name}'."
                )

            visited = set()
            related_collections = {}

            def collect_relations(coll_name):
                if coll_name in visited:
                    return
                visited.add(coll_name)
                related_collections[coll_name] = db[coll_name]
                for field_meta in db[coll_name].values():
                    if isinstance(field_meta, dict) and "ref" in field_meta:
                        ref_collection = field_meta["ref"][0]
                        if ref_collection in db:
                            collect_relations(ref_collection)

            collect_relations(collection_name)

        # Format for LLM: schema + relationship list
        schema_description = ""
        for coll_name, fields in related_collections.items():
            schema_description += f"\n📂 {coll_name}:\n"
            for field, meta in fields.items():
                type_info = meta["type"]
                ref_info = (
                    f" (refers to {meta['ref'][1]} in {meta['ref'][0]})"
                    if "ref" in meta
                    else ""
                )
                schema_description += f"  - {field}: {type_info}{ref_info}\n"

        # Add relation info
        relations = self.relations.get(db_name, [])
        if relations:
            schema_description += f"\n🔗 Relationships in {db_name}:\n"
            for rel in relations:
                schema_description += f"  - {rel['from']}.{rel['local_field']} → {rel['foreign_collection']}.{rel['foreign_field']}\n"

        return schema_description.strip()
