import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import AgentExecutor
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType


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

        # Initialize the Language Model
        llm = ChatGroq(model="llama3-8b-8192", temperature=0)
        print("LLM initialized.")

        # Create the SQL Database Toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()
        print("SQLDatabaseToolkit and tools created.")

        # Create the SQL Agent Executor
        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True # Set to True to see the agent's thought process 
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

if __name__ == "__main__":
    agent = initialize_langchain_agent()

    if agent:
        print("\n--- AI Agent Ready for Queries (Direct Test) ---")
        print("You can ask questions about the data in the database, across multiple tables.")
        print("Type 'exit' to quit.\n")

        while True:
            user_question = input("Your question: ")
            if user_question.lower() == 'exit':
                print("Exiting agent. Goodbye!")
                break

            try:
                response = agent.invoke({"input": user_question})
                print("\nAgent's Answer:")
                print(response['output'])
                print("-" * 50)
            except Exception as e:
                print(f"An error occurred during agent execution: {e}")
                print("Please try rephrasing your question or check the agent's verbose output for details.")
                print("-" * 50)
    else:
        print("Failed to initialize the AI agent for direct testing.")