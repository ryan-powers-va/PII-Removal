import spacy
from spacy.tokens import DocBin
from spacy.training.example import Example
from tqdm import tqdm
from training_data import TRAINING_DATA

# Step 2: Convert training data to spaCy's format
def convert_data_to_spacy_format(data):
    db = DocBin()
    nlp = spacy.blank("en")  # Create a blank English pipeline
    for text, annotations in tqdm(data):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annotations["entities"]:
            span = doc.char_span(start, end, label=label)
            if span:
                ents.append(span)
        doc.ents = ents
        db.add(doc)
    return db

# Convert and save data
train_db = convert_data_to_spacy_format(TRAINING_DATA)
train_db.to_disk("./train.spacy")  # Save training data

# Step 3: Create a blank pipeline and add the NER component
nlp = spacy.blank("en")
ner = nlp.add_pipe("ner", last=True)

# Add the PERSON label to the NER pipeline
ner.add_label("PERSON")

# Step 4: Train the model
def train_ner(nlp, training_data_path, output_dir, n_iter=30):
    # Load training data
    db = DocBin().from_disk(training_data_path)
    
    # Convert to Spacy's Example objects
    train_examples = []
    for doc in db.get_docs(nlp.vocab):
        example = Example.from_dict(doc, {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]})
        train_examples.append(example)

    # Disable other pipeline components during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        for i in range(n_iter):
            losses = {}
            for example in tqdm(train_examples):
                example = Example.from_dict(nlp.make_doc(example.text), example.to_dict())
                nlp.update([example], losses=losses)
            print(f"Iteration {i + 1}, Losses: {losses}")

    # Save the trained model
    nlp.to_disk(output_dir)
    print(f"Model saved to {output_dir}")

# Train the model
train_ner(nlp, "./train.spacy", "./custom_ner_model")
