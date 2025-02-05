import streamlit as st
import google.generativeai as genai
import base64
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Load environment variables from the .env file
load_dotenv()

# Configure API Key
API_KEY = st.secrets["API_KEY"]

if not API_KEY:
    st.error("API Key is missing. Please check your Streamlit secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# Google Sheets Authentication
def authenticate_google_sheets():
    """Authenticate with Google Sheets using service account credentials."""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
    )
    client = gspread.authorize(credentials)
    return client

# Function to get or create the Google Spreadsheet for login records
def get_or_create_spreadsheet(client):
    """Get or create the Google Spreadsheet to store login records."""
    try:
        spreadsheet = client.open("Chatbot_Login_Records")
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create("Chatbot_Login_Records")
    return spreadsheet

# Function to save login record into Google Spreadsheet
def save_login_record(name, emp_id):
    """Save a new login record into the Google Spreadsheet."""
    client = authenticate_google_sheets()
    spreadsheet = get_or_create_spreadsheet(client)
    worksheet = spreadsheet.sheet1
    new_record = [name, emp_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    try:
        worksheet.append_row(new_record)
    except Exception as e:
        print(f"Error saving record: {e}")

# Function to set background image
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

# Main Streamlit App
def main():
    st.set_page_config(
        page_title="MS FINCAP - Credit Policy Assistant",
        page_icon="💳",
        layout="wide"
    )

    # Session state for login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    st.image("msfincap.png", width=200)
    st.markdown("<h1 class='main-title'>🏦 MS FINCAP YOUR FINANCIAL NAVIGATOR</h1>", unsafe_allow_html=True)

    if not st.session_state.logged_in:
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
    else:
        set_background("background.png")
        
        with st.sidebar:
            st.header("🔍 Chat Controls")
            mode = st.selectbox("Conversation Mode", ["Standard", "Detailed", "Concise"])
            if st.button("🔄 Reset Conversation"):
                st.session_state.messages = []
                st.rerun()
            if st.button("📤 Logout"):
                st.session_state.logged_in = False
                st.session_state.messages = []
                st.rerun()

        credit_policy_text = "Sample credit policy text..."
        if 'messages' not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": f"Hello {st.session_state.user_name}! How can I help?"}]

        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"<div class='user-message'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-message'><strong>Credit Policy Bot:</strong> {message['content']}</div>", unsafe_allow_html=True)

        user_query = st.chat_input("Ask about the credit policy...")
        if user_query:
            st.session_state.messages.append({"role": "user", "content": user_query})
            response = ask_gemini(user_query, credit_policy_text)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()
