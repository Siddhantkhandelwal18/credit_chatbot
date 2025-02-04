import streamlit as st
import google.generativeai as genai
import base64
import os
from dotenv import load_dotenv  # Import python-dotenv

# Load environment variables from the .env file
load_dotenv()

# ✅ Step 1: Configure API Key 
import os
import streamlit as st

# Fetch the API key from Streamlit secrets
API_KEY = st.secrets["API_KEY"]

if not API_KEY:
    st.error("API Key is missing. Please check your Streamlit secrets.")
    st.stop()


genai.configure(api_key=API_KEY) 

# ✅ Step 2: Load the Credit Policy Markdown file 
def load_credit_policy(file_path): 
    """Loads credit policy text from a file, or returns a default message if missing.""" 
    if os.path.exists(file_path): 
        with open(file_path, "r", encoding="utf-8") as file: 
            return file.read() 
    return "No credit policy found. Please upload a policy document." 

# ✅ Function to set background image (Optional)
def set_background(image_path):
    """Sets the background image for the Streamlit app."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url(data:image/png;base64,{encoded_string});
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            .stApp::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                z-index: -1;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# ✅ Step 3: Initialize Gemini Model 
model = genai.GenerativeModel("gemini-pro") 

# ✅ Step 4: Function to Ask Questions 
def ask_gemini(question, credit_policy_text): 
    """Sends a question with the credit policy text to Gemini for a response.""" 
    prompt = f"Use the following credit policy document to answer the question:\n\n{credit_policy_text}\n\nQuestion: {question}" 
    response = model.generate_content(prompt) 
    return response.text if response else "Sorry, I couldn't generate a response." 

# ✅ Function to Load Custom CSS
def load_css():
    """Creates and loads custom CSS for dark theme."""
    css_content = """
    /* Dark Theme for Credit Policy Chatbot */
    :root {
        --background-dark: #121212;
        --background-light: #1E1E1E;
        --text-primary: #FFFFFF;
        --text-secondary: #B0B0B0;
        --accent-color: #BB86FC;
        --user-message-bg: #2C2C2C;
        --bot-message-bg: #1E1E1E;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--background-dark) !important;
        color: var(--text-primary) !important;
    }

    /* Sidebar Styles */
    .css-1aumxhk {
        background-color: var(--background-light) !important;
    }

    /* Main Title */
    .main-title {
        color: var(--accent-color) !important;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(187, 134, 252, 0.3);
    }

    /* Chat Messages */
    .user-message, .bot-message {
        color: var(--text-primary) !important;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 12px;
        max-width: 80%;
        line-height: 1.5;
    }

    .user-message {
        background-color: var(--user-message-bg) !important;
        align-self: flex-end;
        margin-left: auto;
        border-bottom-right-radius: 0;
    }

    .bot-message {
        background-color: var(--bot-message-bg) !important;
        align-self: flex-start;
        margin-right: auto;
        border-bottom-left-radius: 0;
    }

    /* Input Styles */
    .stTextInput > div > div > input {
        color: var(--text-primary) !important;
        background-color: var(--background-light) !important;
        border: 1px solid var(--text-secondary) !important;
    }

    /* Markdown and Text Styles */
    .stMarkdown, 
    .stMarkdown p, 
    .stMarkdown span,
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3 {
        color: var(--text-primary) !important;
    }

    /* Button Styles */
    .stButton > button {
        color: var(--text-primary) !important;
        background-color: var(--accent-color) !important;
        border: none !important;
    }

    /* Select Box Styles */
    .stSelectbox > div > div {
        background-color: var(--background-light) !important;
        color: var(--text-primary) !important;
    }

    /* Spinner and Other Elements */
    .stSpinner > div {
        border-color: var(--accent-color) transparent transparent transparent !important;
    }
    """
    css_file = "dark_theme_styles.css"
    if not os.path.exists(css_file):
        with open(css_file, "w") as f:
            f.write(css_content)

    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ✅ Main Streamlit App
def main():
    # Set page configuration
    st.set_page_config(
        page_title="Credit Policy Assistant", 
        page_icon="💳", 
        layout="wide"
    )

    # Try to set background (optional)
    set_background("background.png")  # If missing, it won't crash

    # Load custom CSS
    load_css()

    # Main Title
    st.markdown("<h1 class='main-title'>🏦 Credit Policy Navigator</h1>", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("🔍 Chat Controls")

        # Conversation Mode Selector
        mode = st.selectbox(
            "Conversation Mode",
            ["Standard", "Detailed", "Concise"],
            help="Choose how detailed you want the responses to be"
        )

        # Clear Chat History
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.experimental_rerun()

    # Load credit policy (from file)
    credit_policy_text = load_credit_policy("Credit_Policy2.md")

    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Hello! I'm your Credit Policy Assistant. How can I help you today?"
            }
        ]

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='user-message'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-message'><strong>Credit Policy Bot:</strong> {message['content']}</div>", unsafe_allow_html=True)

    # Chat input
    user_query = st.chat_input("Ask about the credit policy...")

    # Process user input
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})

        # Adjust response based on mode
        additional_prompt = {
            "Concise": " Please provide a very brief and to-the-point answer.",
            "Detailed": " Please provide a comprehensive and detailed explanation.",
            "Standard": ""
        }.get(mode, "")

        # Generate response
        with st.spinner("Analyzing policy..."):
            response = ask_gemini(user_query + additional_prompt, credit_policy_text)

        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Refresh chat
        st.rerun()

# ✅ Run the Streamlit App
if __name__ == "__main__":
    main()
