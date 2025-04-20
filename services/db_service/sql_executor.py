import mysql.connector
import sqlglot
from sqlglot.errors import ParseError
from config.config import Config
from sqlglot import expressions as exp


def check_sql_syntax(sql_query):
    """
    Checks the syntax of a SQL query using sqlglot.
    """
    try:
        sqlglot.parse_one(sql_query)
        return True
    except ParseError:
        return False


def fix_sql_syntax(sql_query):
    """
    Attempts to fix the syntax of a SQL query using sqlglot.
    """
    try:
        expression = sqlglot.parse_one(sql_query)
        return expression.sql(dialect="mysql")
    except ParseError:
        return None


def rewrite_problematic_subqueries(sql_query):
    """
    Uses sqlglot AST to detect and transform subqueries that use LIMIT inside IN clauses,
    which are not supported by MySQL.
    """
    try:
        expression = sqlglot.parse_one(sql_query)

        for select_node in expression.find_all(exp.Select):
            for in_node in select_node.find_all(exp.In):
                if isinstance(in_node.args.get("expressions"), exp.Subquery):
                    subquery_expr = in_node.args["expressions"].args.get("this")

                    if isinstance(
                        subquery_expr, exp.Select
                    ) and subquery_expr.args.get("limit"):
                        print("🔁 Rewriting IN + LIMIT subquery to JOIN")

                        # Extract the first column used in the subquery
                        subquery_column = subquery_expr.expressions[0]

                        # Alias the subquery as a derived table
                        subquery_alias = exp.Alias(
                            this=subquery_expr, alias=exp.to_identifier("sub")
                        )

                        # Build join condition: original_column = subquery_column
                        join_condition = exp.EQ(
                            this=in_node.args["this"],
                            expression=exp.column("sub", subquery_column.name),
                        )

                        # Replace IN expression with a JOIN
                        join = exp.Join(
                            this=subquery_alias, on=join_condition, kind="INNER"
                        )

                        # Remove the original WHERE ... IN(...) condition
                        if select_node.args.get("where"):
                            original_where = select_node.args["where"]
                            if original_where.find(in_node):
                                select_node.set("where", None)

                        # Add the JOIN
                        if "joins" in select_node.args:
                            select_node.args["joins"].append(join)
                        else:
                            select_node.set("joins", [join])

        return expression.sql(dialect="mysql")

    except Exception as e:
        print(f"⚠️ AST transformation failed: {e}")
        return sql_query


class MySQLExecutor:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=Config.MYSQL["host"],
            user=Config.MYSQL["user"],
            password=Config.MYSQL["password"],
            port=Config.MYSQL["port"],
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query, db_name=None):
        try:
            print("📥 Received query:", query)

            # Step 1: Syntax check and fix
            if not check_sql_syntax(query):
                print("⚠️ Syntax issue detected. Attempting to fix...")
                fixed_query = fix_sql_syntax(query)
                if fixed_query:
                    print("✅ Query fixed by sqlglot:", fixed_query)
                    query = fixed_query
                else:
                    return {
                        "error": "SQL syntax is invalid and could not be fixed.",
                        "query": query,
                    }

            # Step 2: Rewrite AST to fix incompatible structures
            rewritten_query = rewrite_problematic_subqueries(query)
            if rewritten_query != query:
                print("🧠 Rewritten query (AST):", rewritten_query)
                query = rewritten_query

            cursor = self.connection.cursor(dictionary=True)

            if db_name:
                print(f"🔀 Switching to database: {db_name}")
                cursor.execute(f"USE {db_name}")

            cursor.execute(query)

            if query.strip().lower().startswith("select"):
                results = cursor.fetchall()
                print(f"✅ Returned {len(results)} rows")
                return results

            self.connection.commit()
            return {"status": "success"}

        except Exception as e:
            print(f"❌ Error during SQL execution: {str(e)}")
            return {"error": str(e), "query": query}

        finally:
            cursor.close()


sql_executor = MySQLExecutor()
