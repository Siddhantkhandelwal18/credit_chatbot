import streamlit as st
import google.generativeai as genai
import base64
import os
import pandas as pd
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configure API Key
API_KEY = st.secrets["API_KEY"]

if not API_KEY:
    st.error("API Key is missing. Please check your Streamlit secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# MySQL database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="siddhant18",
        database="Siddhant"
    )

# Function to load or create login records from the database
def load_login_records():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Employee_ID, Login_Time FROM LoginRecords")
    records = cursor.fetchall()
    conn.close()
    
    # Return the records as a DataFrame
    return pd.DataFrame(records, columns=['Name', 'Employee_ID', 'Login_Time'])

# Function to save login records into the database
def save_login_record(name, emp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO LoginRecords (Name, Employee_ID, Login_Time) VALUES (%s, %s, %s)", (name, emp_id, timestamp))
    conn.commit()
    conn.close()

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

# Load the Credit Policy Markdown file
def load_credit_policy(file_path):
    """Loads credit policy text from a file, or returns a default message if missing."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return "No credit policy found. Please upload a policy document."

# Function to set background image
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

# Initialize Gemini Model
model = genai.GenerativeModel("gemini-pro")

# Function to Ask Questions
def ask_gemini(question, credit_policy_text):
    """Sends a question with the credit policy text to Gemini for a response."""
    prompt = f"Use the following credit policy document to answer the question:\n\n{credit_policy_text}\n\nQuestion: {question}"
    response = model.generate_content(prompt)
    return response.text if response else "Sorry, I couldn't generate a response."

# Function to Load Custom CSS
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

# Main Streamlit App
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
    st.image("msfincap.png", width=200)

    # Display main title
    st.markdown("<h1 class='main-title'>🏦 MS FINCAP YOUR FINANCIAL NAVIGATOR</h1>", unsafe_allow_html=True)

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
                st.rerun()
            else:
                st.error("Please enter both Name and Employee ID")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Try to set background
        set_background("background.png")

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
                st.rerun()

            # Logout Button
            if st.button("📤 Logout"):
                st.session_state.logged_in = False
                st.session_state.messages = []
                st.rerun()

        # Load credit policy
        credit_policy_text = load_credit_policy("Credit_Policy2.md")

        # Initialize chat history
        if 'messages' not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": f"Hello {st.session_state.user_name}! How can I assist you today?"
                }
            ]
        
        # Display chat history
        for message in st.session_state.messages:
            if message['role'] == 'user':
                st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)

        # User input box
        user_input = st.text_input("Ask your question", key="user_input", placeholder="Type your question here...")

        if st.button("Send", key="send_button"):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})

                # Get response from Gemini model
                response = ask_gemini(user_input, credit_policy_text)
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Display new response
                st.rerun()

# Run the main function to start the app
if __name__ == "__main__":
    main()
