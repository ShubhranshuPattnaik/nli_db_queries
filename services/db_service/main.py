from services.db_service.sql_executor import sql_executor
# from services.db_service.mongo_executor import mongo_executor
from services.chatbot_service.main import query_generator

class QueryService:
    def process_query(self, nl_query):
        """
        Processes a natural language query by determining DBMS, generating a query, and executing it.
        :param nl_query: The natural language query (including DBMS)
        :return: Query execution result or error
        """
        dbms_type, generated_query = query_generator.generate_query(nl_query)
        if dbms_type == "mysql":
            return sql_executor.execute_query(generated_query)
        # elif dbms_type == "mongodb":
        #     return mongo_executor.execute_query(generated_query)
        else:
            return generated_query  # Returns error message if DBMS type is unsupported

query_service = QueryService()
