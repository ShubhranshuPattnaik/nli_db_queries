# demo_query.py

DEMO_QUERIES = {
    "-list paper ids from cora database that are cited more than 3 times, sorted by the number of times they are cited (descending), showing only the top 10 results.": {
        "dbms_type": "sql",
        "db_name": "CORA",
        "query": "SELECT c.citing_paper_id AS paper_id FROM cites c GROUP BY c.citing_paper_id HAVING COUNT(*) > 3 ORDER BY COUNT(*) DESC LIMIT 10;"
    },

    "-list each client and the number of loans they have, but include only those clients who have at least one loan from financial database.": {
        "dbms_type": "sql",
        "db_name": "financial",
        "query": "SELECT c.client_id, COUNT(*) AS loan_count FROM client c JOIN disp d ON c.client_id = d.client_id JOIN loan l ON d.account_id = l.account_id GROUP BY c.client_id HAVING loan_count >= 1 ORDER BY loan_count DESC;"
    },

    "-list the next 10 clients after skipping the first 10, including their district names from financial database.": {
    "dbms_type": "sql",
    "db_name": "financial",
    "query": "SELECT c.client_id, d2.A2 AS district_name FROM client c JOIN district d2 ON c.district_id = d2.district_id ORDER BY c.client_id LIMIT 10 OFFSET 10;"
},

    "-show the average loan payment for each loan status in the financial database.": {
        "dbms_type": "sql",
        "db_name": "financial",
        "query": "SELECT l.status, AVG(l.payments) AS avg_payment FROM loan l GROUP BY l.status;"
    }
}
