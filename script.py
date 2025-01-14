import pandas as pd
import re
import spacy
import os
from transformers import pipeline

# Load spaCy and Hugging Face NER model
def get_spacy_model():
    try:
        # Use __file__ if available, fallback to current working directory
        script_dir = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
        model_path = os.path.join(script_dir, "spacy/data/en_core_web_sm/en_core_web_sm-3.8.0")
        return spacy.load(model_path)
    except OSError as e:
        raise RuntimeError(f"Failed to load spaCy model: {e}")

# Hugging Face NER Pipeline
ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", aggregation_strategy="simple")

# Function to remove PII from text
def remove_pii(text):
    if not isinstance(text, str):
        return text

    # Regular expressions for different types of PII
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    ssn_regex = r'\b(\d{3}-\d{2}-\d{4}|\d{9})\b'
    address_regex = r'\d+\s+[a-zA-Z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Square|Sq)\b'
    phone_regex = r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b'

    # Redact PII using regex substitutions
    text = re.sub(email_regex, '[EMAIL REDACTED]', text)
    text = re.sub(ssn_regex, '[SSN REDACTED]', text)
    text = re.sub(address_regex, '[ADDRESS REDACTED]', text)
    text = re.sub(phone_regex, '[PHONE REDACTED]', text)

    # Function to redact names using spaCy
    def redact_names_spacy(text):
        nlp = get_spacy_model()
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                text = text.replace(ent.text, "[NAME REDACTED]")
        return text

    # Function to target lowercase names using Hugging Face
    def redact_names_huggingface(text):
        text_with_capitalization = text.title()  # Temporarily capitalize for better NER detection
        entities = ner_pipeline(text_with_capitalization)
        for entity in entities:
            if entity['entity_group'] == 'PER':  # 'PER' indicates a person name
                text = text.replace(entity['word'].lower(), '[NAME REDACTED]')
        return text

    # Redact names using spaCy and Hugging Face
    text = redact_names_spacy(text)
    text = redact_names_huggingface(text)

    return text

# Load Excel file and apply PII removal
def remove_pii_from_excel(input_file, output_file):
    try:
        # Read Excel file into DataFrame
        df = pd.read_excel(input_file)

        # Apply PII removal function to all comments
        if 'comment' in df.columns:
            df['comment'] = df['comment'].apply(remove_pii)
        else:
            print("No 'comment' column found in the Excel file.")
            return

        # Save the cleaned DataFrame to a new Excel file
        df.to_excel(output_file, index=False)
        print(f"PII removed and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_file = 'PII_test_2.xlsx'
output_file = 'cleaned_user_comments.xlsx' 
remove_pii_from_excel(input_file, output_file)

