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

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def load_credit_policy(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return "No credit policy found. Please upload a policy document."

def set_background(image_path):
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

def load_css():
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

    /* Login Page Styles */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: var(--background-light);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .login-title {
        text-align: center;
        color: var(--accent-color);
        margin-bottom: 2rem;
    }

    .company-logo {
        display: block;
        margin: 0 auto 2rem auto;
        max-width: 200px;
    }

    /* Existing styles... */
    /* (Keep all your existing CSS styles here) */
    """
    css_file = "dark_theme_styles.css"
    if not os.path.exists(css_file):
        with open(css_file, "w") as f:
            f.write(css_content)

    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def record_login(name, employee_id):
    """Record login information to Excel file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    login_data = {
        'Timestamp': [timestamp],
        'Name': [name],
        'Employee_ID': [employee_id]
    }
    
    excel_file = 'login_records.xlsx'
    
    try:
        # Try to read existing Excel file
        existing_df = pd.read_excel(excel_file)
        new_df = pd.DataFrame(login_data)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    except FileNotFoundError:
        # Create new Excel file if it doesn't exist
        updated_df = pd.DataFrame(login_data)
    
    # Save to Excel
    try:
        updated_df.to_excel(excel_file, index=False)
        return True
    except Exception as e:
        st.error(f"Error recording login: {str(e)}")
        return False

def login_page():
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
    # Company Logo
    if os.path.exists("company_logo.png"):
        st.image("company_logo.png", use_column_width=True)
    
    st.markdown("<h1 class='login-title'>Welcome to Credit Policy Navigator</h1>", unsafe_allow_html=True)
    
    # Login Form
    name = st.text_input("Name")
    employee_id = st.text_input("Employee ID")
    
    if st.button("Login"):
        if name and employee_id:
            # Record login information
            if record_login(name, employee_id):
                st.success("Login recorded successfully!")
                st.session_state.authenticated = True
                st.session_state.user_name = name
                st.session_state.employee_id = employee_id
                st.experimental_rerun()
            else:
                st.error("Failed to record login information")
        else:
            st.error("Please fill in all fields")
    
    st.markdown("</div>", unsafe_allow_html=True)

def main_chat_interface():
    model = genai.GenerativeModel("gemini-pro")
    
    # Set page configuration
    st.set_page_config(
        page_title="Credit Policy Assistant",
        page_icon="💳",
        layout="wide"
    )

    # Try to set background
    set_background("background.png")

    # Load custom CSS
    load_css()

    # Main Title with user name
    st.markdown(f"<h1 class='main-title'>🏦 Welcome {st.session_state.user_name} to Credit Policy Navigator</h1>", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("🔍 Chat Controls")
        st.write(f"Employee ID: {st.session_state.employee_id}")

        # Conversation Mode Selector
        mode = st.selectbox(
            "Conversation Mode",
            ["Standard", "Detailed", "Concise"],
            help="Choose how detailed you want the responses to be"
        )

        # Logout Button
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.experimental_rerun()

        # Clear Chat History
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.experimental_rerun()

    # Rest of your existing chat interface code...
    # (Keep all your existing chat interface code here)

def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        main_chat_interface()

if __name__ == "__main__":
    main()
