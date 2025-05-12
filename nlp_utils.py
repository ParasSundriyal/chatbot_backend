import spacy

nlp = spacy.load("en_core_web_sm")

# Detect intent based on keywords (can be improved later)
def detect_intent(text):
    if "result" in text.lower():
        return "check_result"
    elif "hostel" in text.lower():
        return "hostel_issue"
    elif "submit complaint" in text.lower() or "raise issue" in text.lower():
        return "raise_grievance"
    elif "status" in text.lower():
        return "check_status"
    return "unknown"

# Extract entities like department or dates
def extract_entities(text):
    doc = nlp(text)
    entities = {ent.label_: ent.text for ent in doc.ents}
    return entities
