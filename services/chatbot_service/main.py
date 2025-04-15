import re
import json
from huggingface_hub import InferenceClient
from config.config import Config

class QueryGenerator:
    def __init__(self):
        """
        Initializes the Hugging Face Inference API for DeepSeek-R1.
        """
        self.client = InferenceClient(
            provider="sambanova",
            api_key=Config.HUGGINGFACE_API_KEY,
        )
        self.model = "deepseek-ai/DeepSeek-R1"
        print(f"✅ Using DeepSeek-R1 via Hugging Face API")

    def extract_dbms(self, nl_query): # add logic to extract db name and send it to executor alongside db type
        """
        Extracts the database type (MySQL or MongoDB) from the user's input.
        Supports cases where the DBMS is mentioned at the beginning or end.
        """
        match = re.search(r"\b(mysql|mongodb)\b", nl_query, re.IGNORECASE)
        
        print("match", match)  # Debugging line
        
        if match:
            dbms_type = match.group(1).lower()
            cleaned_query = re.sub(r"\b(mysql|mongodb)\b", "", nl_query, flags=re.IGNORECASE).strip()
            return dbms_type, cleaned_query
        
        return None, nl_query


    def extract_sql_from_response(self, response_text):
        """
        Extracts the SQL query formatted as `{"query": "<SQL_QUERY>"}`
        Ensures only JSON content is extracted and processed.
        """
        try:
            # Find JSON block within response
            json_match = re.search(r"\{.*?\}", response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                json_data = json.loads(json_text)
                if "query" in json_data:
                    return json_data["query"]
        except json.JSONDecodeError:
            pass  # If JSON parsing fails, fallback to regex extraction

        # Fallback: Extract SQL query manually
        sql_match = re.search(r'query:\s*"([^"]+)"', response_text, re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()

        return "ERROR: Could not extract a valid SQL query."

    def generate_query(self, nl_query):
        print("============", nl_query)
        """
        Converts a natural language query into an SQL or MongoDB query using DeepSeek-R1.
        """
        try:
            dbms_type, cleaned_query = self.extract_dbms(nl_query)

            if dbms_type == "mysql":
                prompt = f"""You are an AI that converts natural language queries into valid MySQL queries.
                Return the SQL query inside a JSON object with exactly one key-value pair: `"query": "<SQL_QUERY>"`.
                Do NOT add any explanations, thoughts, or additional text. Just return the JSON.

                **Natural Query**: {cleaned_query}

                **Expected format**:
                ```json
                {{
                    "query": "SELECT * FROM table WHERE condition;"
                }}
                ```"""
            # elif dbms_type == "mongodb":
            #     prompt = f"""You are an AI that converts natural language queries into valid MongoDB queries.
            #     Return the MongoDB query inside a JSON object with exactly one key-value pair: `"query": "<MONGO_QUERY>"`.
            #     Do NOT add any explanations, thoughts, or additional text. Just return the JSON.

            #     **Natural Query**: {cleaned_query}

            #     **Expected format**:
            #     ```json
            #     {{
            #         "query": "db.collection.find({{'key': 'value'}});"
            #     }}
            #     ```"""
            else:
                return None, {"error": "Unsupported or missing DBMS type. Use 'in MySQL' or 'in MongoDB'."}
            
            messages = [{"role": "user", "content": prompt}]
            print("+++++PROmessagesMPT+++++", messages)
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
            )

            response_text = completion.choices[0].message.content
            extracted_query = self.extract_sql_from_response(response_text)
            print("===extracted_query====", extracted_query)
            print(f"🔍 Extracted SQL Query: {extracted_query}")
            return dbms_type, extracted_query

        except Exception as e:
            return None, {"error": "Failed to generate query. Please check the API and input format."}

# Initialize the QueryGenerator globally
query_generator = QueryGenerator()
