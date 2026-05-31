import os
import sqlite3
from groq import Groq
from dotenv import load_dotenv

# Load secret API keys from the .env file
load_dotenv()

# Initialize the Groq Client:
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def run_db_query(sql_query):
    """Executes a SQL query safely on the database and returns data and columns."""
    try:
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        records = cursor.fetchall()
        
        # Extract column names from the executed query metadata
        columns = [description[0] for description in cursor.description] if cursor.description else []
        conn.close()
        return records, columns, None
    except Exception as e:
        return None, None, str(e)

def generate_sql_from_text(user_prompt):
    """Uses Llama-3 to translate English into executable SQLite code."""
    
    # System instructions tell the AI exactly how to behave
    system_instructions = """
    You are an expert AI data analyst specializing in SQLite database structures.
    The database contains a table named 'patients' with the following schema:
    - patient_id (INTEGER PRIMARY KEY)
    - name (TEXT)
    - age (INTEGER)
    - gender (TEXT)
    - disease (TEXT)
    - admission_date (DATE formatted as YYYY-MM-DD)
    - room_number (INTEGER)
    - bill_amount (REAL)

    Your task is to convert the user's natural language request into a working SQLite query.
    
    CRITICAL RULES:
    1. Output ONLY the raw SQL query. Do NOT write explanations, code blocks, or markdown tags like ```sql.
    2. Do not use formatting text or conversational pleasantries. Return only the SQL text.
    3. Use partial string matches like LIKE '%disease%' if the user looks up a dynamic health condition.
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",  # <-- Update this line
            temperature=0.1 
        )
        
        sql_output = response.choices[0].message.content.strip()
        # Clean any accidental markdown output formatting if generated
        if sql_output.startswith("```"):
            sql_output = sql_output.replace("```sql", "").replace("```", "").strip()
        return sql_output
    except Exception as e:
        return f"AI Generation Error: {str(e)}"

def generate_text_summary(document_text):
    """Uses Llama-3 to handle document parsing and summary generation tasks."""
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional medical..."},
                {"role": "user", "content": document_text}
            ],
            model="llama-3.3-70b-versatile",  # <-- Update this line
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summarization Error: {str(e)}"