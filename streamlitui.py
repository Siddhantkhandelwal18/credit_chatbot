import streamlit as st
import google.generativeai as genai
import base64
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

# Configure API Key
API_KEY = st.secrets["API_KEY"]

if not API_KEY:
    st.error("API Key is missing. Please check your Streamlit secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# Function to load or create login records
def load_login_records():
    if os.path.exists('login_records.xlsx'):
        return pd.read_excel('login_records.xlsx')
    return pd.DataFrame(columns=['Name', 'Employee_ID', 'Login_Time'])

# Function to save login records
def save_login_record(name, emp_id):
    df = load_login_records()
    new_record = pd.DataFrame({
        'Name': [name],
        'Employee_ID': [emp_id],
        'Login_Time': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    df = pd.concat([df, new_record], ignore_index=True)
    df.to_excel('login_records.xlsx', index=False)

# Login page CSS
def load_login_css():
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            background-color: rgba(30, 30, 30, 0.9);
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        .login-header {
            text-align: center;
            color: #BB86FC;
            margin-bottom: 30px;
        }
        .login-input {
            background-color: #2C2C2C;
            color: white;
            border: 1px solid #BB86FC;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 15px;
        }
        .login-button {
            background-color: #BB86FC;
            color: black;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            width: 100%;
        }
        .company-logo {
            position: absolute;
            top: 20px;
            left: 20px;
            max-width: 150px;
        }
        .main-title {
            text-align: center;
            color: #BB86FC;
            font-size: 2.5em;
            margin: 20px 0;
            padding-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# Modified main function
def main():
    st.set_page_config(
        page_title="MS FINCAP - Credit Policy Assistant",
        page_icon="💳",
        layout="wide"
    )

    # Load CSS
    load_css()
    load_login_css()

    # Session state for login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Display logo
    st.markdown(
        """
        <img src="msfincap.png" class="company-logo" alt="MS FINCAP Logo">
        """,
        unsafe_allow_html=True
    )

    # Display main title
    st.markdown("<h1 class='main-title'>MS FINCAP YOUR FINANCIAL NAVIGATOR</h1>", unsafe_allow_html=True)

    if not st.session_state.logged_in:
        # Login page
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("<h2 class='login-header'>Login</h2>", unsafe_allow_html=True)
        
        name = st.text_input("Name", key="login_name")
        emp_id = st.text_input("Employee ID", key="login_emp_id")
        
        if st.button("Login", key="login_button"):
            if name and emp_id:
                save_login_record(name, emp_id)
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.session_state.user_emp_id = emp_id
                st.rerun()  # Updated from st.experimental_rerun()
            else:
                st.error("Please enter both Name and Employee ID")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
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
                st.rerun()  # Updated from st.experimental_rerun()

        # Load credit policy
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
            st.rerun()  # Updated from st.experimental_rerun()

# Run the Streamlit App
if __name__ == "__main__":
    main()
