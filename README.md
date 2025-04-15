project_root/
│
├── api_gateway/       # Handles all API endpoints
├── config/            # Configuration files for DB and LLM setup
├── services/
│   ├── chatbot_service/  # NLP logic and chatbot integration
│   └── db_service/       # DB routing and execution logic
└── README.md

##################################################################
-api_gateway/
Contains all the API route definitions. Acts as the entry point for external requests and routes them to the appropriate service.

-config/
Holds configuration files and constants related to:
Database connections
LLM settings (e.g., OpenAI key, model versions)

-services/
🧠 chatbot_service/
Connects to the LLM or chatbot backend.
Translates natural language queries into structured intents or raw SQL.
Extracts relevant query data.

🗃️ db_service/
Determines which database to query based on context or schema.
Executes SQL queries and handles results.
May also handle schema validation or fallback logic.

##################################################################
-Command to start a server:
python -m uvicorn api_gateway.main:app --reload   

##################################################################
        ##################----WORKFLOW----##################

> User initiates a request via /query API:
$ curl -X POST https://yourdomain.com/query \
  -H "Content-Type: application/json" \
  -d '{"ask": "get active users from last 30 days"}'

━━━━━━━━━━━━━━━━━━━━━━
→ [api_gateway] Incoming request
━━━━━━━━━━━━━━━━━━━━━━
[✔] Route matched: POST /query
[→] Forwarding payload to db_service...

━━━━━━━━━━━━━━━━━━━━━━
→ [db_service] Processing query
━━━━━━━━━━━━━━━━━━━━━━
[INFO] Calling → chat_service to interpret natural language
[INFO] Loading modules: extract_dbms, extract_sql_from_response

━━━━━━━━━━━━━━━━━━━━━━
→ [chat_service] Starting interpretation
━━━━━━━━━━━━━━━━━━━━━━
[chat_service] ⇨ extract_dbms("get active users from last 30 days")
[✔] DBMS Type: postgres
[✔] Target DB: user_metrics

[chat_service] ⇨ Invoking LLM (v3.5-turbo) for SQL generation...
[LLM] → Generating SQL for natural language request...
[LLM] ✔ Response received:
"""
Here's your SQL query:
SELECT COUNT(*) FROM users WHERE last_active >= NOW() - INTERVAL '30 days';
"""

[chat_service] ⇨ extract_sql_from_response(...)
[✔] Extracted SQL:
SELECT COUNT(*) FROM users WHERE last_active >= NOW() - INTERVAL '30 days';

━━━━━━━━━━━━━━━━━━━━━━
→ [db_service] Executing query
━━━━━━━━━━━━━━━━━━━━━━
[INFO] Routing to postgres_executor
[postgres_executor] ⇨ Connecting to DB: user_metrics
[postgres_executor] ⇨ Authenticated successfully
[postgres_executor] ⇨ Running SQL:
SELECT COUNT(*) FROM users WHERE last_active >= NOW() - INTERVAL '30 days';
[✔] Query executed successfully

[postgres_executor] → Result: 1482 active users

━━━━━━━━━━━━━━━━━━━━━━
→ [api_gateway] Sending response
━━━━━━━━━━━━━━━━━━━━━━
[RESPONSE]
{
  "result": 1482,
  "status": "success",
  "query": "SELECT COUNT(*) FROM users WHERE last_active >= NOW() - INTERVAL '30 days';",
  "db": "postgres/user_metrics"
}
##################################################################




To-DO:
1. Add logic to extract table name as well
2. create a file for RAG Prompting and add schema injection
3. integrate deepseek-ai/deepseek-coder-1.3b-instruct. Working sexy for SQL 