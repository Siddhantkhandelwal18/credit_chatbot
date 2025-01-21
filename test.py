import streamlit as st
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import AutoConfig, AutoModelForSequenceClassification
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from googletrans import Translator

# Initialize the translator
translator = Translator()

# Load the model and tokenizer
model_path = "D:\credit_chatbot\credit_chatbot"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)

# Load the label encoder and dataset
df = pd.read_csv("clean_data.csv")  
label_encoder = LabelEncoder()

# Fit the label encoder based on your dataset labels
label_encoder.fit(df['labels'])

# Function to translate text to English (if required)
def translate_to_english(text, user_language):
    if user_language != 'English':
        translated = translator.translate(text, src='hi', dest='en')
        return translated.text
    return text

# Function to translate text to Hindi (if required)
def translate_to_hindi(text, user_language):
    if user_language == 'Hindi':
        translated = translator.translate(text, src='en', dest='hi')
        return translated.text
    return text

# Predict function to interact with the model
def predict(question, model, tokenizer, df, label_encoder):
    # Ensure the model is on the correct device (GPU or CPU)
    device = model.device  # Get the model's device (CUDA or CPU)
    
    # Tokenize the question and move the tensors to the correct device
    inputs = tokenizer(question, truncation=True, padding=True, max_length=128, return_tensors="pt")
    
    # Move the tokenized input tensors to the same device as the model
    inputs = {key: val.to(device) for key, val in inputs.items()}
    
    # Perform inference on the model
    outputs = model(**inputs)
    
    # Get the predicted label index and convert it to the label
    predicted_label_idx = torch.argmax(outputs.logits, dim=1).item()
    predicted_label = label_encoder.inverse_transform([predicted_label_idx])[0]
    
    # Retrieve the corresponding answer in English
    answer = df[df["labels"] == predicted_label]["answers"].iloc[0]
    return answer

# Streamlit UI
st.title("Chatbot Interface")
st.write("Ask a question to the trained chatbot! (Choose Hindi or English)")

# Ask user to choose language
user_language = st.selectbox("Choose your language:", ['English', 'Hindi'])

# Input from the user
user_input = st.text_input("Enter your question:")

if user_input:
    with st.spinner('Processing...'):
        # Step 1: Translate input to English if user chose Hindi
        question_in_english = translate_to_english(user_input, user_language)
        
        # Step 2: Predict the answer based on the English question
        answer_in_english = predict(question_in_english, model, tokenizer, df, label_encoder)
        
        # Step 3: Translate the answer back to Hindi if the user selected Hindi
        final_answer = translate_to_hindi(answer_in_english, user_language)
        
        # Display only the user question and the final translated answer
        st.write(f"Question: {user_input}")
        st.success(f"Answer: {final_answer}")
else:
    st.warning("Please enter a question to get a response!")
