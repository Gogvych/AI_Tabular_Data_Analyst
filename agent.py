import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import AgentExecutor
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.prompts import PromptTemplate


DB_FILE_PATH = 'my_lil.db' 

# Initialize LangChain Components 
def initialize_langchain_agent() -> AgentExecutor | None:
    
    load_dotenv() # Load environment variables from .env file

    try:
        # Directly connect to existing database
        db_engine = create_engine(f'sqlite:///{DB_FILE_PATH}')
        print(f"\nSuccessfully connected to existing database: {DB_FILE_PATH}")

        # Create a SQLDatabase object for LangChain
        db = SQLDatabase(db_engine)
        print(f"\nLangChain SQLDatabase object created for the database.")

        usable_tables = db.get_usable_table_names()
        
        if not usable_tables:
            print(f"WARNING: No usable tables found in '{DB_FILE_PATH}'. "
                  "The AI agent cannot perform analysis without data. "
                  "Please ensure your database contains tables.")
            return None # Return None if no tables are found

        print(f"Usable tables in the database: {usable_tables}")

        preloaded_schema = {}
        for table in usable_tables:
            schema = db.get_table_info([table])
            preloaded_schema[table] = schema
            print(f"Schema for {table} preloaded.")

        schema_text = "\n\n".join(
            f"Table: {table}\n{schema}" for table, schema in preloaded_schema.items()
            )
        
        # Initialize the Language Model
        llm = ChatGroq(model="llama3-8b-8192", temperature=0)
        print("LLM initialized.")

        # Create the SQL Database Toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()
        print("SQLDatabaseToolkit and tools created.")

        CUSTOM_PROMPT_TEMPLATE = f"""
You are an assistant with access to a SQL database.

Database Schema:
{schema_text}

If the question is NOT about data analysis, databases, or querying data:
- Skip the Action/Action Input steps entirely
- Go directly to "Final Answer:" with your response

If the question IS about data, analysis, or the database:
- Use ONLY the tables and columns shown in the schema above
- Use the available tools as normal
- STOP immediately after getting query results - do NOT repeat queries

You have access to the following tools:

{{tools}}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}] (SKIP this line for non-database questions)
Action Input: the input to the action (SKIP this line for non-database questions)
Observation: the result of the action (SKIP this line for non-database questions)
Thought: I now know the final answer (REQUIRED after any Observation)
Final Answer: the final answer to the original input question

CRITICAL: After you see query results in an Observation, you MUST immediately write "Thought: I now know the final answer" and then "Final Answer:". Do NOT repeat queries.

Begin!

Question: {{input}}
{{agent_scratchpad}}"""
        
        custom_prompt = PromptTemplate.from_template(CUSTOM_PROMPT_TEMPLATE)

        # Create the SQL Agent Executor
        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True, # Set to True to see the agent's thought process 
            prompt = custom_prompt,
            max_iterations=5,  # Reduced from 5 to prevent excessive looping
            max_execution_time=30,  # Add time limit
            handle_parsing_errors=True
        )
        print("LangChain SQL Agent Executor created, configured for multi-table interaction.")
        return agent_executor
    
    except Exception as e:
        print(f"Error initializing LangChain components: {e}")
        if "GROQ_API_KEY" in str(e):
            print("Please ensure your GROQ_API_KEY environment variable is set.")
        # Catch SQLAlchemy errors specifically for database connection issues
        elif "sqlalchemy.exc" in str(type(e)):
            print(f"Database connection error: {e}. Please check if '{DB_FILE_PATH}' exists and is a valid SQLite database.")
        return None

