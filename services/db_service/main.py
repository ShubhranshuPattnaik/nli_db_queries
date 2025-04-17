from services.db_service.sql_executor import sql_executor
from services.db_service.mongo_executor import mongo_executor
from services.chatbot_service.main import query_generator

class QueryService:
    def process_query(self, nl_query):
        dbms_type, db_name, generated_query = query_generator.generate_query(nl_query)
        if isinstance(generated_query, dict) and "error" in generated_query:
            return generated_query
        if dbms_type == "sql":
            if isinstance(generated_query, dict) and "info" in generated_query:
                return generated_query
            return sql_executor.execute_query(generated_query, db_name=db_name)
        elif dbms_type == "mongo":
            if isinstance(generated_query, dict) and "info" in generated_query:
                return generated_query
            return mongo_executor.execute_query(generated_query, db_name=db_name)
        return {"error": "Unsupported DBMS or database"}

    def test_db_query(self, raw_query: str, db_name: str = None, dbms_type: str = "sql"):
        if dbms_type == "sql":
            return sql_executor.execute_query(raw_query, db_name=db_name)
        elif dbms_type == "mongo":
            return mongo_executor.execute_query(raw_query, db_name=db_name)
        return {"error": "Unsupported DBMS"}

    def test_llm_query(self, nl_query: str):
        dbms_type, db_name, generated_query = query_generator.generate_query(nl_query)
        return {
            "dbms_type": dbms_type,
            "db_name": db_name,
            "llm_query": generated_query
        }

query_service = QueryService()
