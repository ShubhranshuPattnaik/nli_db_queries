import re
import json
import requests
from services.chatbot_service.schema_loader import SchemaLoader


class QueryGenerator:
    def __init__(self, schema_loader):
        self.model = "deepseek-coder:1.3b-instruct"
        self.api_url = "http://localhost:11434/api/generate"
        self.schema_loader = schema_loader
        print(f"✅ Using {self.model} via local Ollama")

    def extract_info(self, nl_query):
        dbms_match = re.search(r"\b(mysql|mongodb|sql)\b", nl_query, re.IGNORECASE)
        db_match = re.search(r"\b(CORA|financial|imdb_ijs)\b", nl_query, re.IGNORECASE)
        table_match = re.search(r"(from|table|into)\s+([a-zA-Z_][a-zA-Z0-9_]*)", nl_query, re.IGNORECASE)

        dbms_raw = dbms_match.group(1).lower() if dbms_match else None
        dbms_type = (
            "sql" if dbms_raw in ["mysql", "sql"]
            else "mongo" if dbms_raw == "mongodb"
            else None
        )

        db_name = db_match.group(1).lower() if db_match else None
        table_name = table_match.group(2).lower() if table_match else None

        cleaned_query = re.sub(r"\b(mysql|mongodb|CORA|financial|imdb_ijs)\b", "", nl_query, flags=re.IGNORECASE).strip()
        return dbms_type, db_name, table_name, cleaned_query

    def build_sql_prompt(self, nl_question, schema):
        return f"""
You are an AI assistant that generates SQL queries based on user questions and the available database schema.

Use correct table and column names. Write syntactically correct SQL. Don't guess if the column doesn't exist.

---

📦 DATABASE SCHEMA:
{schema}

---

💬 USER QUESTION:
{nl_question}

---

🧾 SQL QUERY:
""".strip()


    def build_mongo_prompt(self, nl_question, schema):
        return f"""
You are an AI assistant that generates MongoDB queries based on user questions and the available collection schema.

Return only this JSON: {{ "query": "<MONGO_QUERY>" }}. Do not explain anything.

---

📦 COLLECTION SCHEMA:
{schema}

---

💬 USER QUESTION:
{nl_question}

---

🧾 MONGODB QUERY:
""".strip()

    def extract_query_from_response(self, response_text):
        try:
            json_match = re.search(r"\{.*?\}", response_text, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group(0))
                if "query" in json_data:
                    return json_data["query"]
        except json.JSONDecodeError:
            pass

        fallback = re.search(r'query\s*:\s*"([^"]+)"', response_text, re.IGNORECASE)
        if fallback:
            return fallback.group(1).strip()

        loose_sql = re.search(r"(?i)(select|db\.[a-z0-9_]+\.(find|aggregate))[^;]*;?", response_text)
        if loose_sql:
            return loose_sql.group(0).strip()

        return "ERROR: Could not extract a valid query."

    def auto_fix_query(self, query: str) -> str:
        """
        Fix common hallucinations: incorrect casing, quotes, aliases, language artifacts.
        """
        if "客户" in query or "交易金额" in query:
            print("⚠️ Detected multilingual aliasing — removing.")
            query = re.sub(r"AS\s*'[^']*'", "", query)

        query = query.replace('"', '')  # Remove double quotes
        query = re.sub(r'(?i)transactions\b', 'trans', query)
        query = re.sub(r'(?i)clients?\b', 'client', query)

        # Clean any unknown alias joins like: transactions table(...) or ClientsTable.
        query = re.sub(r'(?i)\btransactions? table\b', 'trans', query)
        query = re.sub(r'\bclients?table\b', 'client', query)

        return query.strip()

    def sanity_check(self, query: str, known_tables: list, known_columns: list) -> bool:
        """
        Basic sanity check: does the query mention valid tables/columns?
        """
        # Just a basic pattern check — not full SQL parsing
        tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', query.lower())
        bad_tables = [t for t in tokens if t in ["clients", "transactions", "tablename", "table"] and t not in known_tables]
        return len(bad_tables) == 0

    def generate_query(self, nl_query):
        try:
            dbms_type, db_name, table_name, cleaned_query = self.extract_info(nl_query)

            if not dbms_type:
                return None, None, {"error": "Missing DBMS type. Use 'in MySQL' or 'in MongoDB'."}
            if not db_name:
                return None, None, {"error": "Database name (CORA, financial, imdb_ijs) not specified."}

            schema = self.schema_loader.get_schema(db_name, table_name)
            known_tables = list(self.schema_loader.schemas[db_name].keys())
            known_columns = []  # (optional) you can parse them from schema if needed

            prompt = (
                self.build_sql_prompt(cleaned_query, schema)
                if dbms_type == "sql"
                else self.build_mongo_prompt(cleaned_query, schema)
            )

            print("\n📤 PROMPT SENT TO LLM:\n", prompt)

            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            })

            response.raise_for_status()
            response_text = response.json().get("response", "")
            print("\n📥 RAW RESPONSE FROM LLM:\n", response_text)

            extracted_query = self.extract_query_from_response(response_text)
            print("🧾 Extracted Query:", extracted_query)

            # 🧠 Auto-fix hallucinated output
            cleaned_query = self.auto_fix_query(extracted_query)

            # ✅ Optional: block hallucinated queries
            if not self.sanity_check(cleaned_query, known_tables, known_columns):
                return dbms_type, db_name, {
                    "error": "Detected hallucinated or invalid table names.",
                    "query": cleaned_query
                }

            return dbms_type, db_name, cleaned_query

        except Exception as e:
            return None, None, {"error": f"Failed to generate query: {str(e)}"}


# Global init
schema_loader = SchemaLoader()
query_generator = QueryGenerator(schema_loader)
