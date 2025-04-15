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
        # add logic to get db name
        if dbms_type == "mysql":
            return sql_executor.execute_query(generated_query)
        # elif dbms_type == "mongodb":
        #     return mongo_executor.execute_query(generated_query)
        else:
            return generated_query  # Returns error message if DBMS type is unsupported

    #####################################
    ######<<<<<THIS IS A TEST FUNCTION TO TEST QUERY IS BEING EXECUTED >>>>>######
    def test_db_query(self, raw_sql: str):
        """
        Directly executes a raw SQL query (for testing).
        :param raw_sql: Raw SQL string
        :return: Execution result
        """
        return sql_executor.execute_query(raw_sql)


query_service = QueryService()
