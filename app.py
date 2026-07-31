import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import os

# 1. Securely load the API key from Streamlit Secrets
API_KEY = st.secrets["GEMINI_API_KEY"] 

# 2. Shem Silva Technologies Core Rules
# We removed the hard-coded prices here because the AI will now read them from your CSV.
COMPANY_KNOWLEDGE = """
Company Name: Shem Silva Technologies
Website: https://www.shemsilvatech.com/

Operational Rules for AI:
- You are a professional, corporate AI assistant and quoting engine for Shem Silva Technologies.
- Always refer to the 'Pricing & Services Database' provided below to answer questions about capabilities and quotes.
- If a user uploads an image/document, analyze it to determine if our capabilities can fulfill their requirements based on the database.
- Provide professional insights based ONLY on the provided database.
- If a request falls outside these guidelines or the database, state that human consultation is required.
"""

# 3. Dynamic Database Loader (Reads your Excel/CSV file)
csv_database = ""
if os.path.exists("pricing.csv"):
    try:
        with open("pricing.csv", "r", encoding="utf-8") as file:
            csv_database = file.read()
    except Exception as e:
        pass # If the file has an error, it will just skip reading it safely

# Combine the rules with your actual Excel data
FULL_SYSTEM_PROMPT = COMPANY_KNOWLEDGE + "\n\n### Pricing & Services Database ###\n" + csv_database

# 4. Initialize the AI Client
client = genai.Client(api_key=API_KEY)

# 5. Branded Streamlit Website Setup
st.set_page_config(page_title="Shem Silva Technologies AI", page_icon="💼", layout="centered")

col1, col2 = st.columns([1, 4])

with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=85)
    else:
        st.write(" ")

with col2:
    st.title("Shem Silva Technologies")

st.markdown("### Corporate AI Assistant & Quoting Engine")
st.markdown("Ask questions about our capabilities, or upload your project requirements for a quick analysis.")
st.divider()

# 6. Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 7. Multimodal File Uploader
uploaded_file = st.file_uploader("Upload an image or requirement document (JPG, PNG)", type=["jpg", "jpeg", "png"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 8. Chat Logic
if prompt := st.chat_input("How can we help optimize your business today?"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_contents = [prompt]
    
    if uploaded_file is not None:
        try:
            image = PIL.Image.open(uploaded_file)
            api_contents.append(image)
            st.toast("Requirement document attached!", icon="✅")
        except Exception as e:
            st.error(f"Error processing image: {e}")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # The AI now uses FULL_SYSTEM_PROMPT which contains your CSV data
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=api_contents,
                config=types.GenerateContentConfig(
                    system_instruction=FULL_SYSTEM_PROMPT,
                    temperature=0.2 
                )
            )
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"System Error: {e}")
