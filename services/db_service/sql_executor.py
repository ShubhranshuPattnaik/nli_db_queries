import mysql.connector
from config.config import Config

class MySQLExecutor:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=Config.MYSQL["host"],
            user=Config.MYSQL["user"],
            password=Config.MYSQL["password"],
            port=Config.MYSQL["port"]
            # ❌ removed 'database' — we’ll switch dynamically
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query, db_name=None):
        """
        Executes a SQL query. Optionally selects the DB using USE <db_name>.
        """
        try:
            print("📥 Received query:", query)
            if db_name:
                print(f"🔀 Switching to database: {db_name}")
                self.cursor.execute(f"USE {db_name}")

            self.cursor.execute(query)

            if query.strip().lower().startswith("select"):
                results = self.cursor.fetchall()
                print(f"✅ Returned {len(results)} rows")
                return results

            self.connection.commit()
            return {"status": "success"}

        except Exception as e:
            print(f"❌ Error during SQL execution: {str(e)}")
            return {"error": str(e), "query": query}

sql_executor = MySQLExecutor()
