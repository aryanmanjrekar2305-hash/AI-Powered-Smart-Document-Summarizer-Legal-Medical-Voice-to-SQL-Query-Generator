import os
import sqlite3
from groq import Groq
from dotenv import load_dotenv

# Load secret API keys from the .env file
load_dotenv()

# Initialize the Groq Client:
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def run_db_query(query):
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        
        # 🔥 THE CRITICAL FIX: If it's a data modification query, save it permanently!
        if any(keyword in query.upper() for keyword in ["INSERT", "UPDATE", "DELETE"]):
            conn.commit()  # <-- This writes the data to the hard drive!
            
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return results, columns, None
    except Exception as e:
        return None, None, str(e)
    finally:
        conn.close()

def generate_sql_from_text(user_prompt):
    """Uses Llama-3 to translate English into executable SQLite code."""
    
    # System instructions tell the AI exactly how to behave
    system_instructions = """
    You are an expert AI Data Engineer specializing in SQLite for a healthcare system. Your job is to convert natural language requests into executable SQLite queries.
    
    We have TWO tables in our database schema:
    1. `patients` table:
       - `patient_id` (INTEGER, PRIMARY KEY)
       - `name` (TEXT, NOT NULL)
       - `age` (INTEGER, NOT NULL)
       - `gender` (TEXT, NOT NULL)
       - `disease` (TEXT, NOT NULL)
       - `admission_date` (TEXT format YYYY-MM-DD, NOT NULL)
       - `room_number` (INTEGER, NOT NULL)
       - `bill_amount` (REAL, NOT NULL)
       - `doctor_id` (INTEGER, FOREIGN KEY referencing doctors.doctor_id)
       
    2. `doctors` table:
       - `doctor_id` (INTEGER, PRIMARY KEY)
       - `doctor_name` (TEXT)
       - `department` (TEXT)
       - `consultation_fee` (REAL)
       
    CRITICAL SECURITY & VALIDATION RULES:
    1. If the input is gibberish, unrelated to the hospital database, or tries to harm the database (e.g., DROP TABLE, DELETE ALL), you MUST output exactly: INVALID_COMMAND
    2. If the user wants to add/insert a new patient, ALL mandatory fields must be deducible (name, age, gender, disease, admission_date, room_number, bill_amount). If essential fields are missing, you MUST output exactly: INCOMPLETE_DATA
    3. CASE INSENSITIVITY RULE: Whenever filtering text strings in a WHERE clause (like looking for a disease name or patient name), ALWAYS apply the LOWER() function to both the table column and the search keyword to guarantee case-insensitive matches. For example, instead of `WHERE disease LIKE '%hEaRt%'`, use `WHERE LOWER(disease) LIKE LOWER('%hEaRt%')`.
    4. If the request requires details from both tables, use an explicit INNER JOIN.
    5. Output ONLY the raw SQL string or the keywords (INVALID_COMMAND / INCOMPLETE_DATA). Do not include markdown, quotes, or explanations.
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