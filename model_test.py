import pandas as pd
import spacy

# Load the custom NER model
nlp = spacy.load("./custom_ner_model")

# Function to remove PII from text using the custom NER model
def remove_pii(text):
    if not isinstance(text, str):
        return text

    # Analyze the text for named entities
    doc = nlp(text)

    # Replace detected PERSON entities with a placeholder
    redacted_text = text
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            redacted_text = redacted_text.replace(ent.text, "[NAME REDACTED]")

    return redacted_text

# Load Excel file and process comments
def remove_pii_from_excel(input_file, output_file):
    try:
        # Read Excel file into DataFrame
        df = pd.read_excel(input_file)

        # Apply PII removal function to all comments
        if "comments" in df.columns:
            df["comments"] = df["comments"].apply(remove_pii)
        else:
            print("No 'comments' column found in the Excel file.")
            return

        # Save the cleaned DataFrame to a new Excel file
        df.to_excel(output_file, index=False)
        print(f"PII removed and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_file = "PII_Test_File.xlsx"  # Replace with your input file name
output_file = "cleaned_user_comments.xlsx"  # Replace with your desired output file name
remove_pii_from_excel(input_file, output_file)