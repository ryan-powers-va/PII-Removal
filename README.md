## Description
This script removes Personally Identifiable Information (PII) from text data in an Excel file. It identifies and redacts the following types of PII:

- Email Addresses: Replaces with [EMAIL REDACTED].
- Social Security Numbers (SSN): Replaces with [SSN REDACTED].
- Addresses: Replaces with [ADDRESS REDACTED].
- Names: Uses both spaCy and Hugging Face to identify and replace names with [NAME REDACTED], including lowercase names.

## How It Works
### Regex Matching:
Detects and redacts structured PII (emails, SSNs, addresses, phone numbers) using regular expressions.

### spaCy for Name Redaction:
Identifies and redacts names using Named Entity Recognition (NER) for capitalized names.

### Hugging Face for Lowercase Names:
Detects lowercase names by temporarily capitalizing the text for NER processing.

## Excel Integration:
- Reads an input Excel file.
- Applies the PII removal logic to the 'comment' column.
- Saves the cleaned data to a new Excel file.
## Usage
- Use VSCode or similar environment. 
- Input File: Place your PII in an excel file column named 'comment' (or rename the column with PII), replace the input file name (bottom of script.py file) with the name of the file containing PII. 
- Run the script.
- Output File: The cleaned Excel file will be saved with redacted PII in the same folder as your input file.

## Requirements
You may get errors if you don't have required packages downloaded. 
- Python (avoid the absolute latest version and check the compatability of the libraries - I used 3.11 with this script which is a stable version with robust compatibility - past versions available on Python website).
- The **requirements.txt** file should be all you need, it includes the spaCy language model via url. 
#### Libraries:
To run this script, you need to install the following Python packages:

- pandas: For working with Excel files and data manipulation.
- spacy: For advanced NLP tasks, such as recognizing names.
- transformers: From Hugging Face, for state-of-the-art Named Entity Recognition (NER).
- openpyxl: Required by pandas for reading and writing Excel files.

### **Install pandas, spacy, transformers, and openpyxl:** 
pip install pandas spacy transformers openpyxl
### **Download the spaCy language model:** 
python -m spacy download en_core_web_sm
