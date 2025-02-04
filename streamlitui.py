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

def get_base64_logo():
    """Convert logo image to base64 string"""
    with open("company_logo.png", "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

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
    /* Colorful Theme for Credit Policy Chatbot */
    :root {
        --primary-color: #4CAF50;
        --secondary-color: #2196F3;
        --accent-color: #FF4081;
        --background-color: #F5F5F5;
        --text-primary: #333333;
        --text-secondary: #666666;
        --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        --gradient-bg: linear-gradient(135deg, #4CAF50, #2196F3);
    }

    /* Login Page Styles */
    .main-container {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        background: var(--background-color);
    }

    .top-bar {
        background: var(--gradient-bg);
        padding: 1rem;
        display: flex;
        align-items: center;
        box-shadow: var(--box-shadow);
    }

    .company-logo {
        width: 150px;
        height: auto;
        margin-right: 1rem;
    }

    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: var(--box-shadow);
        animation: fadeIn 0.5s ease-in-out;
    }

    .login-title {
        text-align: center;
        color: var(--primary-color);
        margin-bottom: 2rem;
        font-size: 1.8rem;
        font-weight: bold;
    }

    /* Input Field Styles */
    .stTextInput > div > div > input {
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2) !important;
    }

    /* Button Styles */
    .stButton > button {
        background: var(--gradient-bg) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: bold !important;
        transition: transform 0.2s ease !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
    }

    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Error/Success Messages */
    .stAlert {
        border-radius: 8px !important;
        animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
        from { transform: translateX(-10px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
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
    # Main container
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # Top bar with logo
    st.markdown("""
        <div class='top-bar'>
            <img src='data:image/png;base64,{0}' class='company-logo' alt='Company Logo'>
        </div>
    """.format(get_base64_logo() if os.path.exists("company_logo.png") else ""), unsafe_allow_html=True)
    
    # Login container
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
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
                st.rerun()
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
            st.rerun()

        # Clear Chat History
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.rerun()

    # Rest of your existing chat interface code...
    # (Keep all your existing chat interface code here)

def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        main_chat_interface()

if __name__ == "__main__":
    main()
