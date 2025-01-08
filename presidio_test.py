import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Initialize Presidio Analyzer and Anonymizer
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Function to remove PII from text using Presidio
def remove_pii(text):
    if not isinstance(text, str):
        return text

    # Analyze the text for PII entities
    analyzer_results = analyzer.analyze(text=text, language='en')

    # Anonymize the detected PII entities
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=analyzer_results)

    return anonymized_text.text

# Load Excel file and process comments
def remove_pii_from_excel(input_file, output_file):
    try:
        # Read Excel file into DataFrame
        df = pd.read_excel(input_file)

        # Apply PII removal function to all comments
        if 'comments' in df.columns:
            df['comments'] = df['comments'].apply(remove_pii)
        else:
            print("No 'comments' column found in the Excel file.")
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
