import re
import json
import requests
from services.chatbot_service.schema_loader import SchemaLoader
from services.chatbot_service.mongo_schema_loader import MongoSchemaLoader
from services.chatbot_service.instruction_loader import InstructionLoader
# from services.chatbot_service.query_generator import QueryGenerator


class QueryGenerator:
    def __init__(
        self, sql_schema_loader, mongo_schema_loader, instruction_loader
    ):
        self.model = "llama3"
        self.api_url = "http://localhost:11434/api/generate"
        self.sql_schema_loader: SchemaLoader = sql_schema_loader
        self.mongo_schema_loader: MongoSchemaLoader = mongo_schema_loader
        self.instruction_loader: InstructionLoader = instruction_loader
        print(f"✅ Using {self.model} via local Ollama")

    def detect_intent(self, nl_query: str):
        intent_map = {
            "schema": [
                "what tables",
                "list tables",
                "attributes of",
                "show schema",
                "describe table",
                "what collections",
                "list all collections",
                "list collections",
                "list the collections",
            ],
            "data": [
                "sample data",
                "show data from",
                "first rows",
                "example rows",
            ],
            "insert": ["add", "insert"],
            "update": ["update"],
            "delete": ["delete", "remove"],
        }
        for intent, phrases in intent_map.items():
            for phrase in phrases:
                if phrase in nl_query.lower():
                    return intent
        return "query"

    def build_prompt(
        self, nl_question, schema, intent, dbms_type, instructions
    ):
        if dbms_type == "mongo":
            if intent == "insert":
                return f"{instructions}\n\nTask: Convert the instruction below into a valid MongoDB `insertOne` query using the provided schema. Schema:\n{schema}\nInstruction: {nl_question}\nMongoDB Query:"
            elif intent == "update":
                return f"{instructions}\n\nConvert the instruction below into a valid MongoDB `updateOne` query using the provided schema. Schema:\n{schema}\nInstruction: {nl_question}\nMongoDB Query:"
            elif intent == "delete":
                return f"{instructions}\n\nConvert the instruction below into a valid MongoDB `deleteOne` query using the provided schema. Schema:\n{schema}\nInstruction: {nl_question}\nMongoDB Query:"
            elif intent == "schema":
                return f"Summarize the collection names and the meta data about the fields present in them of the collections  asked in instruction. using data from {schema}. instruction: {nl_question}"
            elif intent == "data":
                return f"{instructions}\n\nWrite a MongoDB query to return 5 sample documents from the appropriate collection. Schema:\n{schema}\nInstruction: {nl_question}\nMongoDB Query:"
            else:
                return f"{instructions}\n\nConvert the instruction into a **single-line MongoDB query** using either `find()` or `aggregate()`.\nUse `$lookup` only if the instruction requires fields from multiple collections.\nSchema:\n{schema}\nInstruction: {nl_question}\nIMPORTANT: Do not hardcode any ID values like director_id or movie_id. If a name is given, use a subquery or lookup to find the ID.\nMongoDB Query:"
        else:
            # Add MySQL 8.0.32 tag to every SQL prompt
            mysql_header = "Use MySQL version 8.0.32 syntax. Do not use features unsupported in this version.\n"

            if intent == "insert":
                return f"{mysql_header}Convert the following to a valid SQL INSERT query. Schema:\n{schema}\nInstruction: {nl_question}\nSQL:"
            elif intent == "update":
                return f"{mysql_header}Convert the following to a valid SQL UPDATE query. Schema:\n{schema}\nInstruction: {nl_question}\nSQL:"
            elif intent == "delete":
                return f"{mysql_header}Convert the following to a valid SQL DELETE query. Schema:\n{schema}\nInstruction: {nl_question}\nSQL:"
            elif intent == "schema":
                return f"{mysql_header}List tables and fields from this schema:\n{schema}"
            elif intent == "data":
                return f"{mysql_header}Generate a SQL query to return 5 sample rows. Schema:\n{schema}\nInstruction: {nl_question}\nSQL:"
            else:
                return f"{mysql_header}Convert the following natural language question into an optimized MySQL 8.0.32-compatible SQL query. Schema:\n{schema}\nQuestion: {nl_question}\nSQL:"

    def extract_info(self, nl_query):
        dbms_match = re.search(
            r"\b(mysql|mongodb|sql)\b", nl_query, re.IGNORECASE
        )
        db_match = re.search(
            r"\b(CORA|financial|imdb_ijs)\b", nl_query, re.IGNORECASE
        )
        table_match = re.search(
            r"\btable-([a-zA-Z_][a-zA-Z0-9_]*)", nl_query, re.IGNORECASE
        )

        dbms_raw = dbms_match.group(1).lower() if dbms_match else None
        dbms_type = (
            "sql"
            if dbms_raw in ["mysql", "sql"]
            else "mongo"
            if dbms_raw == "mongodb"
            else "sql"  # Default to SQL if not specified
        )

        db_name = db_match.group(1).lower() if db_match else None
        table_name = table_match.group(1).lower() if table_match else None

        # ⛔️ Do NOT clean the query – send it as-is to the LLM
        cleaned_query = nl_query.strip()

        return dbms_type, db_name, table_name, cleaned_query

    def generate_query(self, nl_query):
        try:
            intent = self.detect_intent(nl_query)
            dbms_type, db_name, table_name, cleaned_query = self.extract_info(
                nl_query
            )
            if not db_name:
                return (
                    None,
                    None,
                    {
                        "error": "Missing DB name (e.g., CORA, financial, imdb_ijs)."
                    },
                )

            # ⬇️ Handle schema intent directly without calling LLM
            if intent == "schema":
                if dbms_type == "sql":
                    if not table_name:
                        # Return just table names
                        table_names = list(
                            self.sql_schema_loader.schemas.get(
                                db_name, {}
                            ).keys()
                        )
                        return dbms_type, db_name, {"tables": table_names}
                    else:
                        related_schema = self.sql_schema_loader.schemas.get(
                            db_name, {}
                        ).get(table_name)
                        if related_schema:
                            field_lines = [
                                line.strip("- ").strip()
                                for line in related_schema.strip().splitlines()
                                if "-" in line
                            ]
                            return dbms_type, db_name, {"fields": field_lines}
                        else:
                            return (
                                dbms_type,
                                db_name,
                                {
                                    "error": f"No schema found for table '{table_name}'"
                                },
                            )

                elif dbms_type == "mongo":
                    if not table_name:
                        # Return just collection names
                        collection_names = list(
                            self.mongo_schema_loader.schema.get(
                                db_name, {}
                            ).keys()
                        )
                        return (
                            dbms_type,
                            db_name,
                            {"collections": collection_names},
                        )
                    else:
                        related_schema: str = (
                            self.mongo_schema_loader.schema.get(
                                db_name, {}
                            ).get(table_name)
                        )
                        if related_schema:
                            field_lines = [
                                line.strip("- ").strip()
                                for line in related_schema.strip().splitlines()
                                if "->" in line or ":" in line
                            ]
                            return dbms_type, db_name, {"fields": field_lines}
                        else:
                            return (
                                dbms_type,
                                db_name,
                                {
                                    "error": f"No schema found for collection '{table_name}'"
                                },
                            )

            schema = (
                self.sql_schema_loader.get_schema(db_name, table_name)
                if db_name == "sql"
                else self.mongo_schema_loader.get_schema(
                    db_name, collection_name=table_name
                )
            )
            instructions = self.instruction_loader.mongo_instructions
            prompt = self.build_prompt(
                cleaned_query, schema, intent, dbms_type, instructions
            )

            print("\n📤 PROMPT SENT TO LLM:\n", prompt)
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
            )

            response.raise_for_status()
            response_text = response.json().get("response", "").strip()
            # Remove LLM explanations and markdown formatting if present
            code_block = re.search(
                r"```(?:sql)?\n(.*?)```", response_text, re.DOTALL
            )
            if code_block:
                response_text = code_block.group(1).strip()
            else:
                response_text = (
                    re.sub(r"(?i)^Here is .*?SQL query:\n", "", response_text)
                    .strip()
                    .split("Explanation:")[0]
                    .strip()
                )
            print("\n📥 RAW RESPONSE FROM LLM:\n", response_text)

            if dbms_type == "sql" and db_name:
                response_text = re.sub(
                    r"\bdb\.([a-zA-Z_][a-zA-Z0-9_]*)",
                    f"{db_name}.\\1",
                    response_text,
                )

            return dbms_type, db_name, response_text

        except Exception as e:
            return None, None, {"error": f"Failed to generate query: {str(e)}"}


sql_schema_loader = SchemaLoader()
mongo_schema_loader = MongoSchemaLoader()
instruction_loader = InstructionLoader()
query_generator = QueryGenerator(
    sql_schema_loader, mongo_schema_loader, instruction_loader
)
