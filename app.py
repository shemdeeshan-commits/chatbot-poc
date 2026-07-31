import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import os

# 1. Securely load the API key from Streamlit Secrets
API_KEY = st.secrets["GEMINI_API_KEY"] 

# 2. Shem Silva Technologies Core Rules
COMPANY_KNOWLEDGE = """
Company Name: Shem Silva Technologies
Website: https://www.shemsilvatech.com/

Operational Rules for AI:
- You are a professional, corporate AI assistant for Shem Silva Technologies.
- Use the 'Company Background Info' to answer general questions about leadership, history, and operations.
- Use the 'Pricing & Services Database' to answer questions about specific capabilities and quotes.
- If a user uploads an image/document, analyze it to determine if our capabilities can fulfill their requirements.
- If a request falls entirely outside both databases, state that human consultation is required.
"""

# 3. Load Pricing Database (CSV)
csv_database = ""
if os.path.exists("pricing.csv"):
    try:
        with open("pricing.csv", "r", encoding="utf-8", errors="replace") as file:
            csv_database = file.read()
    except Exception as e:
        pass

# 4. Load Company Info Database (TXT)
company_info = ""
if os.path.exists("company_info.txt"):
    try:
        with open("company_info.txt", "r", encoding="utf-8", errors="replace") as file:
            company_info = file.read()
    except Exception as e:
        st.error(f"⚠️ I found company_info.txt, but cannot read it. Error: {e}")

# Merge everything into one giant brain for the AI
FULL_SYSTEM_PROMPT = f"""
{COMPANY_KNOWLEDGE}

### Company Background Info ###
{company_info}

### Pricing & Services Database ###
{csv_database}
"""

# 5. Initialize the AI Client
client = genai.Client(api_key=API_KEY)

# 6. Branded Streamlit Website Setup
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

# 7. Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 8. Multimodal File Uploader
uploaded_file = st.file_uploader("Upload an image or requirement document (JPG, PNG)", type=["jpg", "jpeg", "png"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. Chat Logic
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
