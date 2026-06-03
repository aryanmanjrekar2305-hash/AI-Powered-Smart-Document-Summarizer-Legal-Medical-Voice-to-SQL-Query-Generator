import os
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from engine import generate_sql_from_text, run_db_query

# --- PAGE LAYOUT CONFIGURATION ---
st.set_page_config(
    page_title="AI Data Operations Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

from dotenv import load_dotenv

# Load secret API keys from the local hidden .env file
load_dotenv()

# Initialize the Groq Client safely without exposing the string text
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
# --- SIDEBAR DATABASE SCHEMA GUIDE ---
st.sidebar.title("📁 Database Reference Guide")
st.sidebar.markdown("""
**Table Name:** `patients`
                    
**Available Columns:**
* 🆔 `patient_id` (Integer)
* 👤 `name` (Text)
* 🔢 `age` (Integer)
* ⚥ `gender` (Text)
* 🩺 `disease` (Text)
* 📅 `admission_date` (YYYY-MM-DD)
* 🏥 `room_number` (Integer)
* 💵 `bill_amount` (Real)
""")
st.sidebar.info("💡 Try asking: 'Show me the average age of female patients with Heart Attack'")

# --- APP UI HEADER ---
st.title("🤖 4th Gen Multi-Modal AI Interface")
st.subheader("Natural Language Voice-to-SQL Engine & Document Intelligence Tool")

# Establish app navigation tabs
tab1, tab2 = st.tabs(["📊 Natural Language & Voice to SQL", "📄 Document Intelligence Summarizer"])

with tab1:
    st.write("### Speak or Type a Database Search Request")
    st.info("Try saying: 'Show me all male patients with Heart Attack' or 'List patients with a bill over 10000'")
    
    # --- INPUT LAYOUT SECTION ---
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Manual text input entry box
        user_query = st.text_input("Enter query manually:", placeholder="e.g., Show me all male patients with Heart Attack")
        
    with col2:
        st.write("**Voice Input Option**")
        # Renders the browser interactive audio recording switch
        audio = mic_recorder(
            start_prompt="🎵 Record Voice",
            stop_prompt="🛑 Stop Recording",
            key='voice_input'
        )

    # --- PROCESS VOICE AUDIO ---
    if audio and 'bytes' in audio:
        audio_bytes = audio['bytes']
        
        with st.spinner("Transcribing your voice command..."):
            try:
                # Stream binary WAV chunks directly to Groq's cloud transcription API
                transcription = client.audio.transcriptions.create(
                    file=("temp_voice.wav", audio_bytes, "audio/wav"),
                    model="whisper-large-v3",
                    prompt="The audio contains structured natural language commands targeting a healthcare hospital database query tool."
                )
                user_query = transcription.text
                st.info(f"🗣️ Heard via Microphone: \"{user_query}\"")
            except Exception as e:
                st.error(f"Voice Transcription Error: {str(e)}")

    # --- EXECUTE DATAFRAME GENERATION ---
    if user_query:
        st.write(f"**Processing Prompt:** *\"{user_query}\"*")
        
        # Call language processing translator module
        generated_sql = generate_sql_from_text(user_query)
        st.markdown(f"```sql\n{generated_sql}\n```")
        
        # Push query out to SQLite disk engine
        results, columns, error = run_db_query(generated_sql)
        
        if error:
            st.error(f"SQL execution failure: {error}")
        elif results:
            df = pd.DataFrame(results, columns=columns)
            st.success(f"Found {len(results)} matches!")
            
            # KPI Metrics Block
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label="Total Patients Listed", value=len(df))
            with c2:
                if 'bill_amount' in df.columns:
                    total_bill = f"${df['bill_amount'].sum():,.2f}"
                    st.metric(label="Total Combined Billings", value=total_bill)
                    
            # Future-proofed widescreen layout width syntax
            st.dataframe(df, width='stretch')
        else:
            st.warning("Query executed cleanly but no records matched the system parameters.")

with tab2:
    st.write("### Document Intelligence Component")
    st.info("Upload administrative summaries or medical transcripts below to run automated text abstractions.")
