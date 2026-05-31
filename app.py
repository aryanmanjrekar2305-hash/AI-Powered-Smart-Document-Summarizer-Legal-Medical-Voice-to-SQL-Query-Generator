import streamlit as saved_stream
import speech_recognition as sr
from PyPDF2 import PdfReader
from engine import generate_sql_from_text, run_db_query, generate_text_summary

saved_stream.set_page_config(page_title="AI Data Operations Hub", layout="wide")
saved_stream.title("🤖 4th Gen Multi-Modal AI Interface")
saved_stream.subheader("Natural Language Voice-to-SQL Engine & Document Intelligence Tool")

# Split features into 2 presentation tabs
tab1, tab2 = saved_stream.tabs(["📊 Natural Language & Voice to SQL", "📄 Document Intelligence Summarizer"])

with tab1:
    saved_stream.write("### Speak or Type a Database Search Request")
    saved_stream.info("Try saying: 'Show me all male patients with Heart Attack' or 'List patients with a bill over 10000'")

    col1, col2 = saved_stream.columns([4, 1])
    user_query = ""

    with col1:
        text_input = saved_stream.text_input("Enter query manually:", placeholder="Type here...")
        if text_input:
            user_query = text_input

    with col2:
        saved_stream.write("Voice Input Option")
        if saved_stream.button("🎙️ Trigger Microphone"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                saved_stream.write("Listening closely... Speak into your mic now.")
                try:
                    audio_capture = recognizer.listen(source, timeout=4)
                    user_query = recognizer.recognize_google(audio_capture)
                    saved_stream.success(f"Captured: '{user_query}'")
                except Exception:
                    saved_stream.error("Audio recording failed or timed out. Try again.")

    if user_query:
        saved_stream.write(f"**Processing Prompt:** *\"{user_query}\"*")
        
        # Process language through the engine logic
        generated_sql = generate_sql_from_text(user_query)
        
        saved_stream.markdown(f"```sql\n{generated_sql}\n```")
        
        # Execute query statement against storage
        results, columns, error = run_db_query(generated_sql)
        
        if error:
            saved_stream.error(f"SQL execution failure: {error}")
        elif results:
            saved_stream.success(f"Found {len(results)} matches!")
            # Use pandas structure format directly for seamless visualization layout
            import pandas as pd
            df = pd.DataFrame(results, columns=columns)
            saved_stream.dataframe(df, use_container_width=True)
        else:
            saved_stream.warning("Query executed cleanly but no records matched the conditions.")

with tab2:
    saved_stream.write("### Drop a Document to Analyze and Summarize Text")
    uploaded_file = saved_stream.file_uploader("Upload a medical transcript or corporate text file (PDF or TXT)", type=["pdf", "txt"])
    
    if uploaded_file:
        extracted_content = ""
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                extracted_content += page.extract_text() or ""
        else:
            extracted_content = uploaded_file.read().decode("utf-8")
            
        if extracted_content:
            saved_stream.success("File uploaded successfully!")
            with saved_stream.spinner("Llama-3 generating analysis summary points..."):
                summary_output = generate_text_summary(extracted_content)
                saved_stream.write("#### 📝 Executive Summary Analysis")
                saved_stream.info(summary_output)