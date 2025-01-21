from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import AutoConfig, AutoModelForSequenceClassification
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from googletrans import Translator

# Initialize the Flask app
app = Flask(__name__)

# Initialize the translator
translator = Translator()

# Load the model and tokenizer
model_path = "D:\credit_chatbot\credit_chatbot"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)

# Load the label encoder and dataset
df = pd.read_csv("clean_data.csv")
label_encoder = LabelEncoder()
label_encoder.fit(df['labels'])

# Function to translate text to English
def translate_to_english(text, user_language):
    if user_language != 'English':
        translated = translator.translate(text, src='hi', dest='en')
        return translated.text
    return text

# Function to translate text to Hindi
def translate_to_hindi(text, user_language):
    if user_language == 'Hindi':
        translated = translator.translate(text, src='en', dest='hi')
        return translated.text
    return text

# Predict function
def predict(question, model, tokenizer, df, label_encoder):
    device = model.device  # Get the model's device (CUDA or CPU)
    inputs = tokenizer(question, truncation=True, padding=True, max_length=128, return_tensors="pt")
    inputs = {key: val.to(device) for key, val in inputs.items()}
    outputs = model(**inputs)
    predicted_label_idx = torch.argmax(outputs.logits, dim=1).item()
    predicted_label = label_encoder.inverse_transform([predicted_label_idx])[0]
    answer = df[df["labels"] == predicted_label]["answers"].iloc[0]
    return answer

# Flask route for WhatsApp webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()  # User's message
    user_language = 'Hindi' if 'Hindi' in request.values.get('ProfileName', '') else 'English'  # Language detection
    
    # Translate input to English if needed
    question_in_english = translate_to_english(incoming_msg, user_language)
    
    # Get the chatbot response
    answer_in_english = predict(question_in_english, model, tokenizer, df, label_encoder)
    
    # Translate answer back to the user's language
    final_answer = translate_to_hindi(answer_in_english, user_language)
    
    # Send the response back to WhatsApp
    response = MessagingResponse()
    response.message(final_answer)
    return str(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
