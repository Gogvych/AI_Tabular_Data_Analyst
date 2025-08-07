from fastapi import FastAPI, HTTPException, File, UploadFile
import pandas as pd
import sqlite3
from pydantic import BaseModel
import uvicorn
import tempfile
import os

# Import the AI agent initialization function from agent.py
# The function now handles table discovery, so we don't pass a table name
from agent import initialize_langchain_agent
from langchain.agents import AgentExecutor # Import AgentExecutor for type hinting

# Global variable to hold the initialized agent
agent_instance: AgentExecutor | None = None
DB_FILE_PATH = 'my_lil.db'

# FastAPI App Initialization
app = FastAPI(
    title="AI Tabular Data Analyst API",
    description="An API to serve an AI agent that analyzes tabular data via SQL queries using LangChain and Groq LLM."
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for incoming query requests
class QueryRequest(BaseModel):
    question: str

# FastAPI Event Handler
@app.on_event("startup")
async def startup_event():
    global agent_instance # Declare intent to modify the global variable
    print("FastAPI application startup event: Initializing AI agent...")
    agent_instance = initialize_langchain_agent() # Call the function from agent.py
    if agent_instance is None:
        print("WARNING: AI agent failed to initialize. API endpoints may not function correctly.")

# FastAPI Endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = filename.split(".")[-1].lower()
    if ext not in ("csv", "xlsx"):
        raise HTTPException(status_code=400, detail="Only CSV or XLSX files are allowed.")

    tmp_path = None
    conn = None
    try:
        # Read the file content asynchronously
        file_contents = await file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(file_contents)
            tmp_path = tmp.name

        if ext == "csv":
            df = pd.read_csv(tmp_path, encoding='latin1')
        else:
            df = pd.read_excel(tmp_path)

        # Use a dynamic table name from the filename
        table_name = os.path.splitext(os.path.basename(filename))[0].replace(" ", "_").replace("-", "_")
        # Ensure it's a valid SQL table name
        if not table_name:
            raise ValueError("Could not determine a valid table name from the filename.")
            
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()

        # --- FIX: Drop all existing tables before uploading new data ---
        # Get a list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Loop through the tables and drop each one
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
            print(f"Dropped old table: {table[0]}")

        # Use the dynamic table name when writing to the database
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.commit()

        # We don't need to re-initialize the agent here because it can discover new tables
        print(f"File '{filename}' uploaded. Data saved to table '{table_name}'.")

        # --- FIX: Re-initialize the agent so it's aware of the new table structure ---
        global agent_instance
        agent_instance = initialize_langchain_agent()
        if agent_instance is None:
             raise Exception("Failed to re-initialize AI agent after upload.")

        return {"detail": f"File '{filename}' uploaded and data saved successfully to table '{table_name}'."}
    except Exception as e:
        if conn:
            conn.rollback() # Rollback changes if an error occurs
        if "ValueError" in str(e):
            raise HTTPException(status_code=400, detail=f"Error processing file name: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")
    finally:
        if conn:
            conn.close()
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@app.post("/query")
async def process_query(request: QueryRequest):
    
    if agent_instance is None:
        raise HTTPException(status_code=503, detail="AI agent is not initialized. Please check server logs.")

    try:
        print(f"\nReceived query: {request.question}")
        # Invoke the agent with the user's question
        response = agent_instance.invoke({"input": request.question})
        print(f"Agent's response: {response['output']}")
        return {"answer": response['output']}
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your query: {e}")

# Main Execution Block for Uvicorn 
if __name__ == "__main__":
    print("Starting FastAPI application...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
