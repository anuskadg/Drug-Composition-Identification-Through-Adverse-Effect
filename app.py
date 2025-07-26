from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pickle
import torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini model
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
#app.secret_key = "supersecretkey"  # Needed for session

# Load BERT model for disease prediction
MODEL_PATH = "./bert_model"
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Load encoders and medicine data
with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

with open("side_effect_data.pkl", "rb") as f:
    side_effect_data = pickle.load(f)

severity_mapping = side_effect_data["severity_mapping"]
side_effect_categories = side_effect_data["side_effect_categories"]
medicine_df = pd.read_excel("D3K.xlsx")

def is_medical_query(user_input):
    medical_keywords = [
        "symptom", "disease", "medicine", "treatment", "doctor", "side effect",
        "health", "prescription", "diagnosis", "fever", "pain", "infection", "tablet",
        "dose", "syrup", "vaccine", "illness", "hospital", "clinic", "therapy",
        "medication", "allergy", "chronic", "acute", "dizziness", "nausea", "paracetamol"
    ]
    return any(word in user_input.lower() for word in medical_keywords)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    symptoms = request.form.get("symptoms", "")

    if not symptoms:
        return render_template("result.html", error="No symptoms provided!")

    inputs = tokenizer(symptoms, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)

    predicted_label = torch.argmax(outputs.logits, dim=1).item()
    disease_name = label_encoder.inverse_transform([predicted_label])[0]
    medicine_details = get_medicine_details(disease_name)

    return render_template(
        "result.html",
        predicted_disease=disease_name,
        medicine_recommendations=medicine_details,
        symptoms=symptoms
    )

def get_medicine_details(disease_name):
    medicines_info = medicine_df.loc[
        medicine_df["Disease Name"].str.lower().str.strip() == disease_name.lower().strip(),
        ["Medicine Name", "Side Effects", "Composition"]
    ].dropna()

    if medicines_info.empty:
        return [{"message": f"No recommended medicines found for {disease_name}"}]

    result = []
    for _, row in medicines_info.iterrows():
        medicine_name = row["Medicine Name"].strip()
        composition = row["Composition"].strip()
        side_effects = [effect.strip().lower() for effect in str(row["Side Effects"]).split(", ")]

        severity_levels = [sev for sev, effects in severity_mapping.items() if any(effect in effects for effect in side_effects)]
        severity_label = ", ".join(severity_levels) if severity_levels else "Unknown"

        categorized = {
            category: [effect for effect in side_effects if any(effect in s for s in effects)]
            for category, effects in side_effect_categories.items()
        }
        categorized_cleaned = {k: v for k, v in categorized.items() if v}

        result.append({
            "medicine_name": medicine_name,
            "composition": composition,
            "side_effects": side_effects,
            "severity_level": severity_label,
            "categorized_side_effects": categorized_cleaned
        })

    return result

@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"response": "Please enter a valid question."})
    
    if not is_medical_query(user_input):
        return jsonify({"response": "I specialize in medical queries. Please ask about symptoms, treatments, or medicines."})
    
    # Add a medical-focused system prompt
    medical_prompt = (
        "You are a medical assistant. Only answer questions related to health, diseases, symptoms, medicines, or treatments. "
        "If the question is not medical, reply: 'Please ask medical-related questions.'\n"
        f"User: {user_input}"
    )
    response_text = get_gemini_response(medical_prompt)
    return jsonify({"response": response_text})


def get_gemini_response(user_input, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content(contents=user_input)
            if hasattr(response, "text"):
                return response.text
            if hasattr(response, "candidates"):
                return response.candidates[0].content.parts[0].text
            return str(response)
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Error: {str(e)}"
            time.sleep(delay)

if __name__ == '__main__':
    app.run(debug=True)