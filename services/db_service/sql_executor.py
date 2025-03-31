import mysql.connector
from config.config import Config

class MySQLExecutor:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=Config.MYSQL["host"],
            user=Config.MYSQL["user"],
            password=Config.MYSQL["password"],
            database=Config.MYSQL["database"]
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query):
        try:
            print("=======",query )
            self.cursor.execute(query)
            if query.lower().startswith("select"):
                return self.cursor.fetchall()
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return query

sql_executor = MySQLExecutor()
