import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import torch
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import random

# =========================================
# Step 1: Load and Double the Dataset
# =========================================
def augment_data(df):
    augmented_data = []
    for _, row in df.iterrows():
        # Convert the row to a dictionary
        original_row = row.to_dict()
        augmented_data.append(original_row)

        # Create a synthetic variation of the question
        synthetic_question = row["questions"].replace("What", "Tell me about").replace("How", "Explain").replace("Can", "Is it possible to")
        augmented_row = original_row.copy()
        augmented_row["questions"] = synthetic_question

        # Append the synthetic row
        augmented_data.append(augmented_row)

    return pd.DataFrame(augmented_data)


# Load dataset
df = pd.read_csv("clean_data.csv")  # Ensure columns are `questions`, `answers`, `labels`

# Double the dataset
df_augmented = augment_data(df)

# Encode labels
label_encoder = LabelEncoder()
df_augmented["label_encoded"] = label_encoder.fit_transform(df_augmented["labels"])

# Split into train and validation sets
train_df, val_df = train_test_split(df_augmented, test_size=0.2, random_state=42)

# Save label mapping for later
label_mapping = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))

# =========================================
# Step 2: Tokenize Questions
# =========================================
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def tokenize_data(dataframe):
    return tokenizer(list(dataframe["questions"]), truncation=True, padding=True, max_length=128, return_tensors="pt")

train_encodings = tokenize_data(train_df)
val_encodings = tokenize_data(val_df)

# Convert labels to tensors
train_labels = torch.tensor(list(train_df["label_encoded"]))
val_labels = torch.tensor(list(val_df["label_encoded"]))

# =========================================
# Step 3: Define the Dataset Class
# =========================================
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item

train_dataset = CustomDataset(train_encodings, train_labels)
val_dataset = CustomDataset(val_encodings, val_labels)

# =========================================
# Step 4: Load Pre-trained BERT Model
# =========================================
num_labels = len(label_mapping)  # Number of unique labels
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=num_labels)

# =========================================
# Step 5: Define Training Arguments
# =========================================
training_args = TrainingArguments(
    output_dir="./results",          # Directory to save model checkpoints
    evaluation_strategy="epoch",    # Evaluate at the end of each epoch
    learning_rate=2e-5,             # Learning rate
    per_device_train_batch_size=16, # Batch size for training
    per_device_eval_batch_size=16,  # Batch size for evaluation
    num_train_epochs=3,             # Number of epochs
    weight_decay=0.01,              # Weight decay
    logging_dir="./logs",           # Logging directory
    logging_steps=10,
    save_strategy="epoch",          # Save model after each epoch
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

# =========================================
# Step 6: Train the Model
# =========================================
trainer.train()

# =========================================
# Step 7: Save the Fine-Tuned Model
# =========================================
model.save_pretrained("./bert_chatbot_model")
tokenizer.save_pretrained("./bert_chatbot_model")

# =========================================
# Step 8: Inference
# =========================================
def predict(question, model, tokenizer, df, label_encoder):
    # Tokenize the input question
    inputs = tokenizer(question, truncation=True, padding=True, max_length=128, return_tensors="pt")
    outputs = model(**inputs)
    predicted_label_idx = torch.argmax(outputs.logits, dim=1).item()

    # Decode the label and retrieve the answer
    predicted_label = label_encoder.inverse_transform([predicted_label_idx])[0]
    answer = df[df["labels"] == predicted_label]["answers"].iloc[0]
    return answer

# Example inference
question = "What is the interest rate?"
answer = predict(question, model, tokenizer, df, label_encoder)
print(f"Question: {question}\nAnswer: {answer}")
