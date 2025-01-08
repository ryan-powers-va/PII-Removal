import pandas as pd
import re
import spacy

# Function to remove PII from text
nlp = spacy.load("en_core_web_sm")

def remove_pii(text):
    if not isinstance(text, str):
        return text

    # Regular expressions for different types of PII
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    ssn_regex = r'\b(\d{3}-\d{2}-\d{4}|\d{9})\b'
    address_regex = r'\d+\s+[a-zA-Z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Square|Sq)\b'
    # name_regex = r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b'  # Simplified name regex

     # NLP for name detection
    def redact_names(text):
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                text = text.replace(ent.text, "[NAME REDACTED]")
        return text

    # Remove PII using regex substitutions
    text = re.sub(email_regex, '[EMAIL REDACTED]', text)
    text = re.sub(ssn_regex, '[SSN REDACTED]', text)
    text = re.sub(address_regex, '[ADDRESS REDACTED]', text)
    # text = re.sub(name_regex, '[NAME REDACTED]', text)

    # Use spaCy for name redaction
    text = redact_names(text)

    return text

# Load Excel file
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
input_file = 'PII_Test_File.xlsx'  # Replace with your input file name
output_file = 'cleaned_user_comments.xlsx'  # Replace with your desired output file name
remove_pii_from_excel(input_file, output_file)
