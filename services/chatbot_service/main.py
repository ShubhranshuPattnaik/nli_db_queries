import re
import json
import requests
from services.chatbot_service.schema_loader import SchemaLoader

class QueryGenerator:
    def __init__(self, schema_loader):
        self.model = "llama3"
        self.api_url = "http://localhost:11434/api/generate"
        self.schema_loader = schema_loader
        print(f"✅ Using {self.model} via local Ollama")

    def detect_intent(self, nl_query):
        intent_map = {
            "schema": ["what tables", "list tables", "attributes of", "show schema", "describe table", "what collections"],
            "data": ["sample data", "show data from", "first rows", "example rows"],
            "insert": ["add", "insert"],
            "update": ["update"],
            "delete": ["delete", "remove"]
        }
        for intent, phrases in intent_map.items():
            for phrase in phrases:
                if phrase in nl_query.lower():
                    return intent
        return "query"

    def build_prompt(self, nl_question, schema, intent, dbms_type):
        if dbms_type == "mongo":
            if intent == "insert":
                return f"Convert to MongoDB insertOne query. Schema:\n{schema}\nInstruction: {nl_question}\nMongoDB:"
            elif intent == "update":
                return f"Convert to MongoDB updateOne query. Schema:\n{schema}\nInstruction: {nl_question}\nMongoDB:"
            elif intent == "delete":
                return f"Convert to MongoDB deleteOne query. Schema:\n{schema}\nInstruction: {nl_question}\nMongoDB:"
            elif intent == "schema":
                return f"List collections and fields from this schema:\n{schema}"
            elif intent == "data":
                return f"Generate a MongoDB query to return 5 sample rows. Schema:\n{schema}\nInstruction: {nl_question}\nMongoDB:"
            else:
                return f"Generate a MongoDB query (find/aggregate/lookup). Schema:\n{schema}\nInstruction: {nl_question}\nMongoDB:"
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
        dbms_match = re.search(r"\b(mysql|mongodb|sql)\b", nl_query, re.IGNORECASE)
        db_match = re.search(r"\b(CORA|financial|imdb_ijs)\b", nl_query, re.IGNORECASE)
        table_match = re.search(r"\btable-([a-zA-Z_][a-zA-Z0-9_]*)", nl_query, re.IGNORECASE)

        dbms_raw = dbms_match.group(1).lower() if dbms_match else None
        dbms_type = (
            "sql" if dbms_raw in ["mysql", "sql"]
            else "mongo" if dbms_raw == "mongodb"
            else "sql"
        )

        db_name = db_match.group(1).lower() if db_match else None
        table_name = table_match.group(1).lower() if table_match else None

        # ⛔️ Do NOT clean the query – send it as-is to the LLM
        cleaned_query = nl_query.strip()

        return dbms_type, db_name, table_name, cleaned_query

    def generate_query(self, nl_query):
        try:
            intent = self.detect_intent(nl_query)
            dbms_type, db_name, table_name, cleaned_query = self.extract_info(nl_query)
            if not db_name:
                return None, None, {"error": "Missing DB name (e.g., CORA, financial, imdb_ijs)."}

            # ⬇️ Handle schema intent directly without calling LLM
            if intent == "schema":
                if not table_name:
                    # Return just table names
                    table_names = list(self.schema_loader.schemas.get(db_name, {}).keys())
                    return dbms_type, db_name, {"tables": table_names}
                else:
                    related_schema = self.schema_loader.schemas.get(db_name, {}).get(table_name)
                    if related_schema:
                        field_lines = [
                            line.strip("- ").strip()
                            for line in related_schema.strip().splitlines()
                            if "-" in line
                        ]
                        return dbms_type, db_name, {"fields": field_lines}
                    else:
                        return dbms_type, db_name, {"error": f"No schema found for table '{table_name}'"}

            schema = self.schema_loader.get_schema(db_name, table_name)
            prompt = self.build_prompt(cleaned_query, schema, intent, dbms_type)
            print("\n📤 PROMPT SENT TO LLM:\n", prompt)
            response = requests.post(self.api_url, json={"model": self.model, "prompt": prompt, "stream": False})
            response.raise_for_status()
            response_text = response.json().get("response", "").strip()

            code_block = re.search(r"```(?:sql)?\n(.*?)```", response_text, re.DOTALL)
            if code_block:
                response_text = code_block.group(1).strip()
            else:
                response_text = re.sub(r"(?i)^Here is .*?SQL query:\n", "", response_text).strip().split("Explanation:")[0].strip()

            print("\n📥 RAW RESPONSE FROM LLM:\n", response_text)

            if dbms_type == "sql" and db_name:
                response_text = re.sub(r"\bdb\.([a-zA-Z_][a-zA-Z0-9_]*)", f"{db_name}.\\1", response_text)

            return dbms_type, db_name, response_text

        except Exception as e:
            return None, None, {"error": f"Failed to generate query: {str(e)}"}

schema_loader = SchemaLoader()
query_generator = QueryGenerator(schema_loader)
