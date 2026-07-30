import streamlit as st
from google import genai
from google.genai import types
import PIL.Image

# 1. Securely load the API key from Streamlit Secrets
API_KEY = st.secrets["GEMINI_API_KEY"] 

# 2. Add your company details here
COMPANY_KNOWLEDGE = """
Company Name: Your Company Name
Core Capabilities: 
- We provide corporate AI solutions.
- Data analysis and custom integrations.

Quotation & Budget Guidelines:
- Standard Package starts at $500.
- Custom requirements evaluated per project.

Operational Rules for AI:
- You are a helpful assistant for this company.
- If a user uploads an image/document, analyze it to determine if our capabilities can fulfill their requirements.
- Provide estimated quotations based ONLY on the guidelines above.
- If a request falls outside these guidelines, state that human consultation is required.
"""

# 3. Initialize the AI Client
client = genai.Client(api_key=API_KEY)

# 4. Streamlit Website Setup
st.set_page_config(page_title="Company AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 Company AI Assistant & Quoting Engine")
st.markdown("Ask questions about our services, or upload your requirements/images for a quick capability analysis.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Multimodal File Uploader
uploaded_file = st.file_uploader("Upload an image or requirement document (JPG, PNG)", type=["jpg", "jpeg", "png"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Chat Logic
if prompt := st.chat_input("How can we help you today?"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_contents = [prompt]
    
    if uploaded_file is not None:
        try:
            image = PIL.Image.open(uploaded_file)
            api_contents.append(image)
            st.toast("Image attached!", icon="✅")
        except Exception as e:
            st.error("Error processing image.")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=api_contents,
                config=types.GenerateContentConfig(
                    system_instruction=COMPANY_KNOWLEDGE,
                    temperature=0.2 
                )
            )
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("Please check your API key and try again.")
