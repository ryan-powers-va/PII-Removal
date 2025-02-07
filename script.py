import pandas as pd
import re
import spacy
import os
from transformers import pipeline

# Global constants for name detection
WHITELIST = {
    "Veterans", "Veteran", "Veteran's",
    "Medical", "Dental", "Provider", "Providers",
    "Appointment", "Appt", "Department", "Office",
    "Service", "Services", "Center", "Clinic",
    "Hospital", "Health", "Care", "COE", "COE's", "VA", "VA's", "C&P",
    "PCP", "Education Benefits", "Education", "Benefits", "Benefit", "SSN",
    "SCO",
}

COMMON_TERMS = {
    "VA.gov", "USA", "DOD", "COVID", "VBA", "VHA",
    "AM", "PM", "EST", "CST", "MST", "PST",
    "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
    "STATUS", "PENDING", "APPROVED", "DENIED", "ACTIVE", "INACTIVE", "User Friendly",
}

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
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    ssn_regex = r'\b(\d{3}-\d{2}-\d{4}|\d{9})\b'
    # More strict address regex that requires street type and number
    address_regex = (
        r'\b\d+\s+'                           # Street number
        r'(?:[A-Za-z0-9\s.-]+\s+)'           # Street name
        r'(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|'
        r'Lane|Ln\.?|Drive|Dr\.?|Court|Ct\.?|Square|Sq\.?|Way|'
        r'Terrace|Place|Pl\.?)'               # Street type
        r'(?:\s*,?\s*'                        # Optional comma
        r'(?:Apt\.?|Unit|Suite|Rm\.?)?\s*'    # Optional unit type
        r'[A-Za-z0-9-]*)?'                    # Optional unit number
        r'(?:\s*,?\s*[A-Za-z\s]+)?'          # Optional city
        r'(?:\s*,?\s*[A-Z]{2})?'             # Optional state
        r'(?:\s*,?\s*\d{5}(?:-\d{4})?)?'     # Optional ZIP
    )
    phone_regex = r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b'

    # Function to redact names using spaCy
    def redact_names_spacy(text):
        nlp = get_spacy_model()
        doc = nlp(text)
        
        redactions = {}
        
        # First pass: check for labeled names (e.g., "Name: John Doe")
        labeled_name_patterns = [
            r'(?i)Name:\s*([A-Za-z\s.-]+?)(?=\s*,|\s*\n|\s*;|$)',  # Name: John Doe
            r'(?i)Patient:\s*([A-Za-z\s.-]+?)(?=\s*,|\s*\n|\s*;|$)',  # Patient: John Doe
            r'(?i)Client:\s*([A-Za-z\s.-]+?)(?=\s*,|\s*\n|\s*;|$)',  # Client: John Doe
        ]
        
        for pattern in labeled_name_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1).strip()
                if (name and 
                    name not in WHITELIST and 
                    not any(term in name for term in COMMON_TERMS)):
                    redactions[name] = "[NAME REDACTED]"
        
        # Second pass: check for all-caps names
        all_caps_name_pattern = r'\b[A-Z][A-Z]+\s+[A-Z][A-Z]+\b'
        potential_names = re.finditer(all_caps_name_pattern, text)
        for match in potential_names:
            name = match.group()
            words = name.split()
            if (len(words) == 2 and
                all(3 <= len(word) <= 15 for word in words) and
                not any(word in COMMON_TERMS for word in words) and
                not any(word.endswith('ING') for word in words) and
                name not in WHITELIST):
                redactions[name] = "[NAME REDACTED]"
        
        # Third pass: use spaCy entities
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "PER"]:
                if (ent.text in COMMON_TERMS or 
                    ent.text in WHITELIST or
                    any(word in COMMON_TERMS or word in WHITELIST for word in ent.text.split()) or
                    len(ent.text) <= 2):
                    continue
                
                words = ent.text.split()
                if all(word.strip("'s") in WHITELIST for word in words):
                    continue
                
                redactions[ent.text] = "[NAME REDACTED]"
                
                # Also catch possessive forms
                possessive = ent.text + "'s"
                if possessive in text:
                    redactions[possessive] = "[NAME REDACTED]'s"
        
        # Apply all redactions at once, starting with longest matches first
        for original in sorted(redactions.keys(), key=len, reverse=True):
            text = text.replace(original, redactions[original])
        
        return text

    # Function to target lowercase names using Hugging Face
    def redact_names_huggingface(text):
        skip_patterns = [
            r'\b(\d{3}-\d{2}-\d{4}|\d{9})\b',  # SSN pattern
            r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b',  # Phone
            r'\d+[/-]\d+[/-]\d+',  # Dates
            r'\[.*?REDACTED\]',  # Already redacted content
            r'\b[A-Z]{2,}(?:\.[A-Z]{2,})*\b',  # Acronyms like VA.gov
            r'\b[A-Z&]{2,}\b',  # Short acronyms like C&P
        ]
        
        # Skip already redacted content
        if '[REDACTED]' in text:
            already_redacted = re.findall(r'\[.*?REDACTED\]', text)
            placeholder_map = {f"PLACEHOLDER_{i}": redacted for i, redacted in enumerate(already_redacted)}
            
            # Temporarily replace redacted content
            for placeholder, redacted in placeholder_map.items():
                text = text.replace(redacted, placeholder)
        
        # Also process the original text without any case modifications
        entities_original = ner_pipeline(text)
        text_with_capitalization = text.title()
        entities_title = ner_pipeline(text_with_capitalization)
        # Add all-caps version for catching uppercase names
        text_normalized = ' '.join(word.capitalize() for word in text.split())
        entities_normalized = ner_pipeline(text_normalized)
        
        all_entities = entities_original + entities_title + entities_normalized
        all_entities.sort(key=lambda x: len(x['word']), reverse=True)
        processed_names = set()
        
        for entity in all_entities:
            if entity['entity_group'] == 'PER':
                name = entity['word']
                
                # Skip placeholders
                if name.startswith('PLACEHOLDER_'):
                    continue
                
                # Skip if matches any skip patterns
                if any(re.search(pattern, name) for pattern in skip_patterns):
                    continue
                    
                # Skip common terms and abbreviations
                if (name in COMMON_TERMS or 
                    name in WHITELIST or
                    any(word in COMMON_TERMS or word in WHITELIST for word in name.split()) or
                    len(name) <= 2):
                    continue
                
                words = name.split()
                if all(word.strip("'s") in WHITELIST for word in words):
                    continue
                
                if name.lower() in processed_names:
                    continue
                
                pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
                text = pattern.sub('[NAME REDACTED]', text)
                
                possessive_pattern = re.compile(r'\b' + re.escape(name) + r'\'s\b', re.IGNORECASE)
                text = possessive_pattern.sub('[NAME REDACTED]\'s', text)
                
                processed_names.add(name.lower())
        
        # Restore originally redacted content
        if '[REDACTED]' in text:
            for placeholder, redacted in placeholder_map.items():
                text = text.replace(placeholder, redacted)
        
        return text

    # First redact names using spaCy and Hugging Face
    text = redact_names_spacy(text)
    text = redact_names_huggingface(text)

    # Then redact other PII using regex substitutions
    text = re.sub(email_regex, '[EMAIL REDACTED]', text)
    text = re.sub(ssn_regex, '[SSN REDACTED]', text)
    text = re.sub(address_regex, '[ADDRESS REDACTED]', text, flags=re.IGNORECASE)
    text = re.sub(phone_regex, '[PHONE REDACTED]', text)

    return text

# Load Excel file and apply PII removal
def remove_pii_from_excel(input_file, output_file):
    try:
        # Read Excel file into DataFrame
        df = pd.read_excel(input_file)

        # Apply PII removal function to all 'comment' columns
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
input_file = 'PII_Test_File.xlsx'
output_file = 'PII_Test_File_Cleaned.xlsx' 
remove_pii_from_excel(input_file, output_file)

