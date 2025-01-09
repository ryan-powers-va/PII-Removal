## Description
This script removes Personally Identifiable Information (PII) from text data in an Excel file. It identifies and redacts the following types of PII:

- Email Addresses: Replaces with [EMAIL REDACTED].
- Social Security Numbers (SSN): Replaces with [SSN REDACTED].
- Addresses: Replaces with [ADDRESS REDACTED].
- Names: Uses both spaCy and Hugging Face to identify and replace names with [NAME REDACTED], including lowercase names.

## How It Works
### Regex Matching:

Detects and redacts structured PII (emails, SSNs, addresses) using regular expressions.

### spaCy for Name Redaction:
Identifies and redacts names using Named Entity Recognition (NER) for capitalized names.

### Hugging Face for Lowercase Names:
Detects lowercase names by temporarily capitalizing the text for NER processing.

## Excel Integration:
- Reads an input Excel file.
- Applies the PII removal logic to the comment column.
- Saves the cleaned data to a new Excel file.
## Usage
- Input File: Place your Excel file containing PII in a column named comment.
- Run the Script: Update the input_file and output_file variables with your file names.
- Output File: The cleaned Excel file will be saved with redacted PII.

## Requirements
- Python 3.7+
- Libraries:
- pandas
- re
- spacy
- transformers
#### Download spaCy model:
python -m spacy download en_core_web_sm
