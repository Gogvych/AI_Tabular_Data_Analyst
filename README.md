AI Tabular Data Analyst
This repository contains the backend and a simple frontend for an AI-powered data analysis application. The backend is a FastAPI server that ingests tabular data (CSV/XLSX), stores it in a SQLite database, and uses a LangChain agent with a Groq LLM to answer natural language questions about the data. The frontend is a straightforward Next.js chatbot interface.

Features
Data Ingestion: Upload .csv or .xlsx files via a REST API endpoint.

SQL-based Analysis: The AI agent translates natural language queries into SQL to analyze the uploaded data.

Natural Language Interaction: Ask questions about your data in plain English and receive insightful answers.

Frontend is built on Next.js framework.

Prerequisites
To run this application, you will need:

Python 3.9+

Node.js and npm (for the Next.js frontend)

A GROQ_API_KEY for the LangChain agent.

Getting Started
1. Backend Setup
Clone the repository:

git clone <your-repository-url>
cd <your-repository-name>

Set up the Python environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Note: A requirements.txt file containing the necessary packages like fastapi, uvicorn, pandas, langchain, langchain-groq, sqlalchemy, and python-dotenv is required.

Configure your API Key:
Create a .env file in the root directory and add your Groq API key:

GROQ_API_KEY="YOUR_GROQ_API_KEY"

Run the backend server:

python main.py

The FastAPI server will start on http://localhost:8000.

2. Frontend Setup (Next.js)
Assuming your frontend is a standard Next.js app in a sub-directory (e.g., frontend/):

Navigate to the frontend directory:

cd frontend

Install dependencies:

npm install

Configure API endpoint:
The frontend code will need to be configured to make requests to http://localhost:8000. You might need to set an environment variable or modify the fetch calls directly in your code.

Run the frontend:

npm run dev

The Next.js app will be available at http://localhost:3000.

Usage
Start both the backend and frontend servers.

Upload Data: Use the frontend interface to upload a .csv or .xlsx file. This will send the file to the /upload endpoint.

Ask Questions: Once the data is uploaded and the AI agent is initialized, use the chatbot interface to ask questions about your data. For example:

"What is the average sales price?"

"Show me the top 5 products by revenue."

"How many unique customers are there?"

File Structure
main.py: The FastAPI application, defining the API endpoints for file upload and querying.

agent.py: Contains the logic for initializing the LangChain agent, connecting to the SQLite database, and setting up the Groq LLM.

my_lil.db: The SQLite database file created and managed by the application.

.env: Environment file for storing the Groq API key.

frontend/: (Presumed) Directory for the Next.js frontend application.