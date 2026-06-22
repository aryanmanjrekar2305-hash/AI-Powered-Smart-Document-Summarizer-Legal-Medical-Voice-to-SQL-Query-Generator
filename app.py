import os
import sqlite3
import pandas as pd
import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq
from dotenv import load_dotenv
import pypdf # 
import docx2txt
# Load system configuration immediately
load_dotenv()

from engine import generate_sql_from_text, run_db_query

st.set_page_config(
    page_title="Advanced AI Data Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Groq Engine Securely
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# --- SIDEBAR RELATIONAL DATABASE GUIDE ---
st.sidebar.title("📁 Relational Database Guide")
st.sidebar.markdown("""
### 🕒 1. Table: `patients`
* `patient_id` (Int) | `name` (Text)
* `age` (Int) | `gender` (Text)
* `disease` (Text) | `admission_date`
* `room_number` (Int) | `bill_amount` (Real)
* `doctor_id` (Int, Link to Doctors)

### 🥼 2. Table: `doctors`
* `doctor_id` (Int) | `doctor_name` (Text)
* `department` (Text) | `consultation_fee`
""")

st.sidebar.warning("""
💡 **Try Complex Relational JOIN:**
*"Show me patient names alongside their doctor's name and department"*
""")

st.sidebar.success("""
✍️ **Try Data Entry (INSERT):**
*"Add a new patient named Sarah Connor, age 40, female, with Trauma, admitted today, room 501, bill 8500, doctor id 2"*
""")

# --- MAIN APP LAYOUT ---
st.title("🤖 4th Gen Multi-Modal AI Interface")
st.subheader("Relational Voice-to-SQL Engine & Document Intelligence Tool")

tab1, tab2 = st.tabs(["📊 Relational Data Operations Engine", "📄 Document Intelligence Summarizer"])

with tab1:
    st.write("### Speak or Type an Operational Command")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_query = st.text_input("Enter command:", placeholder="Type a search query or an entry check-in command...", key="text_input_field")
    with col2:
        st.write("**Voice Control**")
        audio = mic_recorder(start_prompt="🎵 Record Command", stop_prompt="🛑 Stop Recording", key='voice_input')

    # Process Voice Input
    if audio and 'bytes' in audio:
        audio_bytes = audio['bytes']
        with st.spinner("Transcribing speech..."):
            try:
                transcription = client.audio.transcriptions.create(
                    file=("temp_voice.wav", audio_bytes, "audio/wav"),
                    model="whisper-large-v3",
                    prompt="Medical dashboard commands focusing on SQL queries or inserting new records."
                )
                if transcription.text.strip() and transcription.text.strip().lower() != "thank you.":
                    user_query = transcription.text
                    st.info(f"🗣️ Heard: \"{user_query}\"")
            except Exception as e:
                st.error(f"Voice Transcription Error: {str(e)}")

    # Execute Operations
    if user_query:
        clean_query = user_query.strip().rstrip('.')
        st.write(f"**Processing operational instruction:** *\"{clean_query}\"*")
        
        generated_sql = generate_sql_from_text(clean_query).strip()
        
        # --- LAYER 1: INTENT & SECURITY GUARDRAILS ---
        if "INVALID_COMMAND" in generated_sql:
            st.error("❌ SecOps Block: The system cannot map this instruction to a safe or valid database command.")
        elif "INCOMPLETE_DATA" in generated_sql:
            st.warning("⚠️ Data Entry Error: Missing crucial details (like age, gender, or diagnosis). Please check in with full attributes.")
        else:
            st.markdown(f"```sql\n{generated_sql}\n```")
            
            # Execute query statement against storage
            results, columns, error = run_db_query(generated_sql)
            
            if error:
                st.error(f"Execution Error: {error}")
            else:
                is_insert = any(keyword in generated_sql.upper() for keyword in ["INSERT", "UPDATE", "DELETE"])
                
                if is_insert:
                    st.success("¼ Data successfully committed to database storage!")
                    ref_res, ref_cols, _ = run_db_query("SELECT * FROM patients ORDER BY patient_id DESC LIMIT 3")
                    if ref_res:
                        st.write("### Recent Entries View:")
                        st.dataframe(pd.DataFrame(ref_res, columns=ref_cols), width='stretch')
                
                # --- LAYER 2: CLEAN DATA VIEWING & IDENTATION PATCED ---
                elif results:
                    cleaned_columns = []
                    seen_columns = set()
                    
                    for col in columns:
                        if col in seen_columns:
                            cleaned_columns.append(f"{col}_duplicate")
                        else:
                            cleaned_columns.append(col)
                            seen_columns.add(col)
                    
                    df = pd.DataFrame(results, columns=cleaned_columns)
                    st.success(f"Extracted {len(results)} matches!")
                    
                    # Visual Metric Cards Layout
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(label="Total Records Listed", value=len(df))
                    with c2:
                        # Ensure calculation column exists and contains valid numeric content
                        if 'bill_amount' in df.columns and not df['bill_amount'].isnull().all():
                            total_bill = pd.to_numeric(df['bill_amount'], errors='coerce').sum()
                            st.metric(label="Total Metrics Billing Sum", value=f"${total_bill:,.2f}")
                        else:
                            st.metric(label="Data State", value="Relational View")
                            
                    st.dataframe(df, width='stretch')
                
                # --- LAYER 3: ZERO ROW EMPTY DATASET HANDLER ---
                else:
                    st.warning("🔍 No matching records were discovered within the data tables for this criteria.")
with tab2:
    st.write("### 📄 Multi-Format Document Intelligence Summarizer")
    st.caption("Upload medical reports, PDFs, Word documents, or plain text summaries to extract instant AI insights.")
    
    # File uploader widget
    uploaded_file = st.file_uploader("Upload a file:", type=["pdf", "docx", "txt", "md"])
    
    if uploaded_file is not None:
        try:
            document_text = ""
            file_extension = uploaded_file.name.split(".")[-1].lower()
            
            with st.spinner("Extracting content from file structure..."):
                # Parse PDF Files
                if file_extension == "pdf":
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    text_parts = []
                    for page in pdf_reader.pages:
                        extracted_page_text = page.extract_text()
                        if extracted_page_text:
                            text_parts.append(extracted_page_text)
                    document_text = "\n".join(text_parts)
                
                # Parse Microsoft Word Documents
                elif file_extension == "docx":
                    document_text = docx2txt.process(uploaded_file)
                    
                # Parse Standard Plain Text / Markdown Files
                else:
                    document_text = uploaded_file.read().decode("utf-8")
            
            # Guard checking if text extraction was successful
            if not document_text.strip():
                st.warning("⚠️ The uploaded document appears to be empty or contains scanned images with no selectable text layer.")
            else:
                # Show an expandable view of the extracted plain text
                with st.expander("🔍 View Extracted Text Layer"):
                    st.text_area("File Content Preview:", value=document_text, height=200, disabled=True)
                    
                # Process text with the Groq Large Language Model
                if st.button("✨ Generate Document Intelligence Summary", type="primary"):
                    with st.spinner("Analyzing document structure and distilling insights..."):
                       
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",  # The current active model
                            messages=[
                                {
                                    "role": "system", 
                                    "content": "You are an expert Clinical Informatics AI. Synthesize the provided medical or administrative text into an executive summary with bullet points highlighting key insights, diagnoses, actions, or metrics."
                                },
                                {
                                    "role": "user", 
                                    "content": f"Please summarize the following document:\n\n{document_text}"
                                }
                            ],
                            temperature=0.3
                        )
                        
                        st.success("📝 Analysis Complete!")
                        st.markdown("### 📋 Executive Summary Breakdown")
                        st.markdown(response.choices[0].message.content)
                        
        except Exception as e:
            st.error(f"Failed to process document structure: {str(e)}")