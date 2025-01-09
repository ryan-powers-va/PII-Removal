from transformers import pipeline

# Load a pre-trained NER model
ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", aggregation_strategy="simple")

# Input text with lowercase names
text = "john and mary went to the park in new york."

# Perform NER on lowercase text
# Convert text to proper case temporarily for better NER recognition
text_with_capitalization = text.title()

# Perform NER
entities = ner_pipeline(text_with_capitalization)

# Redact names
redacted_text = text
for entity in entities:
    if entity['entity_group'] == 'PER':  # 'PER' indicates person names
        # Replace names (case insensitive) in the original text
        redacted_text = redacted_text.replace(entity['word'].lower(), '[REDACTED]')

print(redacted_text)
