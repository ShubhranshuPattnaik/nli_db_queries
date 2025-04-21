import time
from services.db_service.sql_executor import sql_executor
from services.db_service.mongo_executor import mongo_executor
from services.chatbot_service.main import query_generator
from demo.demo_query import DEMO_QUERIES  

class QueryService:
    def process_query(self, nl_query):
        if nl_query.strip().startswith("-"):
            key = nl_query.strip().lower()
            if key in DEMO_QUERIES:
                demo = DEMO_QUERIES[key]
                dbms_type = demo.get("dbms_type")
                db_name = demo.get("db_name")
                query = demo.get("query")

                print("⏳ Simulating LLM response for prompt...")
                time.sleep(2)

                if dbms_type == "sql":
                    result = sql_executor.execute_query(query, db_name=db_name)
                elif dbms_type == "mongo":
                    result = mongo_executor.execute_query(query, db_name=db_name)
                else:
                    result = {"error": "Unsupported DBMS in demo query"}

                return {
                    "status": "success",
                    "dbms_type": dbms_type,
                    "db_name": db_name,
                    "query": query,
                    "result": result,
                }

            else:
                return {
                    "status": "error",
                    "query": None,
                    "result": {"error": f"No demo query found for: {key}"},
                }

        dbms_type, db_name, generated_query = query_generator.generate_query(nl_query)

        if isinstance(generated_query, dict) and "error" in generated_query:
            return {
                "status": "error",
                "dbms_type": dbms_type,
                "db_name": db_name,
                "query": None,
                "result": generated_query,
            }

        if isinstance(generated_query, dict) and (
            "info" in generated_query
            or "tables" in generated_query
            or "fields" in generated_query
        ):
            return {
                "status": "info",
                "dbms_type": dbms_type,
                "db_name": db_name,
                "result": generated_query,
            }

        if dbms_type == "sql":
            result = sql_executor.execute_query(generated_query, db_name=db_name)
        elif dbms_type == "mongo":
            result = mongo_executor.execute_query(generated_query, db_name=db_name)
        else:
            result = {"error": "Unsupported DBMS or database"}

        return {
            "status": "success",
            "dbms_type": dbms_type,
            "db_name": db_name,
            "query": generated_query,
            "result": result,
        }

    def test_db_query(self, raw_query: str, db_name: str = None, dbms_type: str = "sql"):
        if dbms_type == "sql":
            return sql_executor.execute_query(raw_query, db_name=db_name)
        elif dbms_type == "mongo":
            return mongo_executor.execute_query(raw_query, db_name=db_name)
        return {"error": "Unsupported DBMS"}

    def test_llm_query(self, nl_query: str):
        dbms_type, db_name, generated_query = query_generator.generate_query(nl_query)
        return {
            "status": "success",
            "dbms_type": dbms_type,
            "db_name": db_name,
            "llm_query": generated_query,
        }


query_service = QueryService()
