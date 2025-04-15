from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.db_service.main import query_service

app = FastAPI()

# Define request model
class QueryRequest(BaseModel):
    nl_query: str

class SQLTestRequest(BaseModel):
    raw_sql: str
    db_name: str | None = None
    dbms_type: str = "sql"

class LLMTestRequest(BaseModel):
    nl_query: str

@app.get("/")
def home():
    return {"message": "Welcome to NLQ Chatbot!"}

@app.post("/query/")
def query_database(request: QueryRequest):
    """
    API endpoint to process a natural language query.
    """
    try:
        result = query_service.process_query(request.nl_query)
        return {"query_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
######################################
#### THIS IS A TEST API TO TEST DB EXECUTION ####
@app.post("/test_db/")
def test_raw_sql(request: SQLTestRequest):
    try:
        result = query_service.test_db_query(
            raw_query=request.raw_sql,
            db_name=request.db_name,
            dbms_type=request.dbms_type
        )
        return {
            "status": "success",
            "executed_query": request.raw_sql,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL Execution Error: {str(e)}")
        
######################################
#### THIS IS A TEST API TO TEST LLM RESPONSE ####
@app.post("/test_llm/")
def test_llm_response(request: LLMTestRequest):
    """
    API endpoint to test LLM-generated query without executing it.
    """
    try:
        result = query_service.test_llm_query(request.nl_query)
        return {
            "status": "success",
            "nl_query": request.nl_query,
            "llm_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation Error: {str(e)}")