TRAINING_DATA = [
    # Common lowercase names
    ("john smith is attending the meeting.", {"entities": [(0, 10, "PERSON")]}),
    ("jane doe sent an email yesterday.", {"entities": [(0, 8, "PERSON")]}),
    ("ryan wehan called this morning.", {"entities": [(0, 10, "PERSON")]}),

    # Contextual diversity
    ("john met with jane yesterday.", {"entities": [(0, 4, "PERSON"), (14, 18, "PERSON")]}),
    ("ryan completed the project with help from john smith.", {"entities": [(0, 4, "PERSON"), (34, 44, "PERSON")]}),
    ("please reach out to lisa white for assistance.", {"entities": [(19, 29, "PERSON")]}),

    # Edge cases
    ("the appointment was made by john.", {"entities": [(27, 31, "PERSON")]}),
    ("lisa helped ryan with the task.", {"entities": [(0, 4, "PERSON"), (12, 16, "PERSON")]}),
    ("emily called for assistance on behalf of ryan.", {"entities": [(0, 5, "PERSON"), (41, 45, "PERSON")]}),

    # Hyphenated and compound names
    ("john-smith attended the meeting.", {"entities": [(0, 10, "PERSON")]}),
    ("mary jane watson was here earlier.", {"entities": [(0, 17, "PERSON")]}),

    # Names with punctuation
    ("call jane, the assistant, to confirm.", {"entities": [(5, 9, "PERSON")]}),
    ("it was handled by john; the team agreed.", {"entities": [(19, 23, "PERSON")]}),

    # Negative samples (no names)
    ("the quick brown fox jumped over the lazy dog.", {"entities": []}),
    ("contact support for assistance with your request.", {"entities": []}),
    ("no updates are available at this time.", {"entities": []}),
]
